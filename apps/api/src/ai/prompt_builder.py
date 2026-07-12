import json
from typing import Any


class PromptBuilder:
    SYSTEM = (
        "Ты эксперт по карточкам товаров Wildberries. Возвращай только валидный JSON без markdown. "
        "Не придумывай характеристики, которых нет во входных данных."
    )

    @staticmethod
    def product_payload(product, **extra: Any) -> str:
        payload = {
            "product": {
                "id": product.id,
                "title": product.title,
                "description": product.description,
                "brand": product.brand,
                "category": product.category,
                "price": product.price,
                "rating": product.rating,
                "reviews_count": product.reviews_count,
            },
            **extra,
        }
        return json.dumps(payload, ensure_ascii=False)

    @classmethod
    def task(cls, task: str) -> str:
        rules = {
            "title": "Сформируй title до 60 символов. JSON: {title, rationale}.",
            "description": "Сформируй продающее описание до 2000 символов. JSON: {description, benefits, warnings}.",
            "keywords": "Подбери до 20 релевантных ключевых слов. JSON: {keywords, negative_keywords}.",
            "improve-card": "Улучши карточку. JSON: {title, description, keywords, benefits, recommendations}.",
            "analyze-product": "Проанализируй карточку. JSON: {score, strengths, weaknesses, recommendations}.",
        }
        return f"{cls.SYSTEM} {rules[task]}"
