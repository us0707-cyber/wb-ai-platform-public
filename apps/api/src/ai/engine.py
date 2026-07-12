import hashlib
import json
from typing import Any

import httpx
from sqlalchemy.orm import Session

from src.ai.prompt_builder import PromptBuilder
from src.ai.providers.local import LocalAIProvider
from src.ai.providers.openai import OpenAIProvider
from src.core.config import settings
from src.models import AICache
from src.repositories.product_repository import ProductRepository


class AIEngine:
    def __init__(self) -> None:
        self.local = LocalAIProvider()
        self.openai = OpenAIProvider()

    def provider(self):
        if settings.ai_provider == "openai" and settings.openai_api_key:
            return self.openai
        return self.local

    @staticmethod
    def _cache_key(task: str, provider: str, model: str, prompt: str) -> str:
        raw = json.dumps({"task": task, "provider": provider, "model": model, "prompt": prompt}, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _local_result(task: str, product, extra: dict[str, Any]) -> dict[str, Any]:
        source = " ".join(filter(None, [product.title, product.description, product.brand, product.category]))
        keywords = LocalAIProvider.keywords(source)
        title = product.title.strip()
        if product.brand and product.brand.lower() not in title.lower():
            title = f"{product.brand} {title}"
        title = title[:60]
        description = product.description.strip()
        benefits = [
            "Понятные характеристики товара",
            "Подходит для ежедневного использования",
            "Удобный выбор для покупки онлайн",
        ]
        if task == "title":
            return {"title": title, "rationale": "Название очищено и дополнено брендом", "mode": "local"}
        if task == "description":
            text = f"{title}. {description} {' '.join(benefits)}".strip()
            return {"description": text[:2000], "benefits": benefits, "warnings": [], "mode": "local"}
        if task == "keywords":
            seed = extra.get("seed_keywords", [])
            return {"keywords": list(dict.fromkeys(seed + keywords))[:20], "negative_keywords": [], "mode": "local"}
        if task == "improve-card":
            text = f"{title}. {description} {' '.join(benefits)}".strip()
            return {
                "title": title,
                "description": text[:2000],
                "keywords": keywords,
                "benefits": benefits,
                "recommendations": ["Добавьте реальные размеры и материалы", "Укажите комплектацию", "Проверьте категорию"],
                "mode": "local",
            }
        score = min(100, round(25 + min(len(title), 60) * 0.5 + min(len(description), 1000) * 0.03 + len(keywords), 1))
        return {
            "score": score,
            "strengths": ["Название заполнено"] if title else [],
            "weaknesses": ["Описание слишком короткое"] if len(description) < 200 else [],
            "recommendations": ["Добавьте конкретные преимущества", "Проверьте ключевые слова"],
            "mode": "local",
        }

    async def run(self, db: Session, *, task: str, product_id: int, user_id: int, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        product = ProductRepository(db).get_owned(product_id, user_id)
        if not product:
            raise LookupError("Товар не найден")
        extra = extra or {}
        prompt = PromptBuilder.product_payload(product, task=task, **extra)
        provider = self.provider()
        model = settings.openai_model if provider.name == "openai" else "deterministic-v1"
        key = self._cache_key(task, provider.name, model, prompt)
        cached = db.query(AICache).filter(AICache.cache_key == key).first()
        if cached:
            return {**cached.response_data, "cached": True}

        if provider.name == "local":
            result = self._local_result(task, product, extra)
        else:
            try:
                result = await provider.generate_json(
                    system=PromptBuilder.task(task), user=prompt, schema_name=task
                )
            except (httpx.HTTPError, ValueError, RuntimeError, json.JSONDecodeError):
                result = self._local_result(task, product, extra)
                result["fallback_reason"] = "provider_error"
        result.update({"task": task, "provider": provider.name, "model": model, "product_id": product.id, "cached": False})
        db.add(AICache(cache_key=key, user_id=user_id, product_id=product.id, task=task, provider=provider.name, model=model, response_data=result))
        db.commit()
        return result


ai_engine = AIEngine()
