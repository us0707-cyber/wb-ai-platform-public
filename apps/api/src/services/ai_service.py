import json
import re
from collections import Counter

import httpx

from src.core.config import settings

STOPWORDS = {"для", "это", "как", "или", "при", "что", "без", "его", "она", "они", "товар", "товара", "ваш", "ваша"}


class AIService:
    async def generate(self, system: str, user: str) -> str:
        if not settings.openai_api_key:
            return ""
        headers = {"Authorization": f"Bearer {settings.openai_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": settings.openai_model,
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": system}]},
                {"role": "user", "content": [{"type": "input_text", "text": user}]},
            ],
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post("https://api.openai.com/v1/responses", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("output_text", "")

    @staticmethod
    def extract_keywords(text: str, limit: int = 20) -> list[str]:
        words = re.findall(r"[а-яА-Яa-zA-Z0-9-]{3,}", text.lower())
        counts = Counter(word for word in words if word not in STOPWORDS)
        return [word for word, _ in counts.most_common(limit)]

    async def seo(self, product, target_audience: str, tone: str) -> dict:
        keywords = self.extract_keywords(f"{product.title} {product.description} {product.category} {product.brand}")
        title = product.title.strip()
        if product.brand and product.brand.lower() not in title.lower():
            title = f"{product.brand} {title}"
        title = title[:60]
        benefits = [
            "Практичный выбор для ежедневного использования",
            "Понятные характеристики и удобство применения",
            "Подходит для покупки в подарок и для себя",
        ]
        description = f"{title}. {product.description.strip()} {' '.join(benefits)}"
        score = min(100, 35 + min(len(title), 60) * 0.45 + min(len(description), 1000) * 0.03 + len(keywords) * 1.2)
        llm = await self.generate(
            "Ты эксперт по SEO карточек Wildberries. Верни JSON с title, description, keywords и recommendations.",
            json.dumps({"product": product.title, "description": product.description, "audience": target_audience, "tone": tone}, ensure_ascii=False),
        )
        if llm:
            try:
                parsed = json.loads(llm)
                return {**parsed, "seo_score": round(score, 1), "mode": "llm"}
            except json.JSONDecodeError:
                pass
        return {
            "title": title,
            "description": description[:2000],
            "keywords": keywords,
            "recommendations": ["Добавьте 5–8 конкретных выгод", "Уберите повторы ключевых слов", "Проверьте соответствие категории"],
            "seo_score": round(score, 1),
            "mode": "local",
        }


ai_service = AIService()
