import re
from collections import Counter
from typing import Any

from src.ai.providers.base import AIProvider

STOPWORDS = {
    "для", "это", "как", "или", "при", "что", "без", "его", "она", "они", "товар",
    "товара", "ваш", "ваша", "на", "по", "из", "к", "в", "и", "с", "а",
}


class LocalAIProvider(AIProvider):
    name = "local"

    @staticmethod
    def keywords(text: str, limit: int = 20) -> list[str]:
        words = re.findall(r"[а-яА-Яa-zA-Z0-9-]{3,}", text.lower())
        counts = Counter(word for word in words if word not in STOPWORDS)
        return [word for word, _ in counts.most_common(limit)]

    async def generate_json(self, *, system: str, user: str, schema_name: str) -> dict[str, Any]:
        # Local fallback is intentionally deterministic and does not require an external API key.
        return {"schema": schema_name, "mode": self.name, "raw_input": user[:500]}
