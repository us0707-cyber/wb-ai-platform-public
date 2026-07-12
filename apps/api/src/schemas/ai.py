from typing import Literal

from pydantic import BaseModel, Field


class AIProductRequest(BaseModel):
    product_id: int
    target_audience: str = "покупатели Wildberries"
    tone: str = "продающий и информативный"
    seed_keywords: list[str] = Field(default_factory=list)


class AIApplyRequest(BaseModel):
    product_id: int
    title: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    keywords: list[str] | None = None


class AIProviderInfo(BaseModel):
    configured_provider: Literal["local", "openai"]
    active_provider: Literal["local", "openai"]
    model: str
    openai_configured: bool
