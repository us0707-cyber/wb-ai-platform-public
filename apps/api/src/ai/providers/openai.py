import json
from typing import Any

import httpx

from src.ai.providers.base import AIProvider
from src.core.config import settings


class OpenAIProvider(AIProvider):
    name = "openai"

    @staticmethod
    def _output_text(payload: dict[str, Any]) -> str:
        if payload.get("output_text"):
            return str(payload["output_text"])

        chunks: list[str] = []
        refusals: list[str] = []
        for item in payload.get("output", []):
            for content in item.get("content", []):
                content_type = content.get("type")
                if content_type in {"output_text", "text"} and content.get("text"):
                    chunks.append(str(content["text"]))
                elif content_type == "refusal" and content.get("refusal"):
                    refusals.append(str(content["refusal"]))

        if refusals:
            raise ValueError("OpenAI отказался выполнить запрос: " + " ".join(refusals))
        if not chunks:
            raise ValueError("OpenAI не вернул текстовый результат")
        return "\n".join(chunks)

    @staticmethod
    def _schema(schema_name: str) -> dict[str, Any]:
        string_array = {"type": "array", "items": {"type": "string"}}
        schemas: dict[str, dict[str, Any]] = {
            "title": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "rationale": {"type": "string"},
                },
                "required": ["title", "rationale"],
                "additionalProperties": False,
            },
            "description": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "benefits": string_array,
                    "warnings": string_array,
                },
                "required": ["description", "benefits", "warnings"],
                "additionalProperties": False,
            },
            "keywords": {
                "type": "object",
                "properties": {
                    "keywords": string_array,
                    "negative_keywords": string_array,
                },
                "required": ["keywords", "negative_keywords"],
                "additionalProperties": False,
            },
            "improve-card": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "keywords": string_array,
                    "benefits": string_array,
                    "recommendations": string_array,
                },
                "required": ["title", "description", "keywords", "benefits", "recommendations"],
                "additionalProperties": False,
            },
            "analyze-product": {
                "type": "object",
                "properties": {
                    "score": {"type": "number", "minimum": 0, "maximum": 100},
                    "strengths": string_array,
                    "weaknesses": string_array,
                    "recommendations": string_array,
                },
                "required": ["score", "strengths", "weaknesses", "recommendations"],
                "additionalProperties": False,
            },
        }
        try:
            return schemas[schema_name]
        except KeyError as exc:
            raise ValueError(f"Неизвестная AI-схема: {schema_name}") from exc

    async def generate_json(self, *, system: str, user: str, schema_name: str) -> dict[str, Any]:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.openai_model,
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": system}]},
                {"role": "user", "content": [{"type": "input_text", "text": user}]},
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": schema_name.replace("-", "_"),
                    "strict": True,
                    "schema": self._schema(schema_name),
                }
            },
        }

        async with httpx.AsyncClient(timeout=settings.ai_request_timeout_seconds) as client:
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            text = self._output_text(response.json())

        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError(f"Invalid {schema_name} response")
        data.setdefault("mode", self.name)
        return data
