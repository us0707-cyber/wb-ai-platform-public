from __future__ import annotations

import httpx

from src.core.config import settings


class WildberriesClient:
    def __init__(self, token: str):
        self.token = token.strip()
        self.headers = {"Authorization": self.token}

    async def ping(self) -> dict:
        if not self.token:
            return {"ok": False, "mode": "demo", "message": "API-токен не указан"}
        try:
            cards = await self.fetch_cards(limit=1)
            return {"ok": True, "status_code": 200, "cards_found": len(cards), "message": "Подключение подтверждено"}
        except httpx.HTTPStatusError as exc:
            return {"ok": False, "status_code": exc.response.status_code, "message": exc.response.text[:300]}
        except httpx.HTTPError as exc:
            return {"ok": False, "message": str(exc)}

    async def fetch_cards(self, limit: int = 100) -> list[dict]:
        if not self.token:
            return []
        url = f"{settings.wb_content_api_base}/content/v2/get/cards/list"
        payload = {"settings": {"cursor": {"limit": min(max(limit, 1), 100)}, "filter": {"withPhoto": -1}}}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
        return data.get("cards", []) or []

    async def fetch_stocks(self, date_from: str = "2020-01-01T00:00:00") -> list[dict]:
        if not self.token:
            return []
        url = f"{settings.wb_statistics_api_base}/api/v1/supplier/stocks"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=self.headers, params={"dateFrom": date_from})
            response.raise_for_status()
            return response.json() or []
