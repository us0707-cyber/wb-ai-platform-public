from pydantic import BaseModel, Field, model_validator


class StoreSyncRequest(BaseModel):
    demo_mode: bool = False


class BulkSEORequest(BaseModel):
    product_ids: list[int] = Field(min_length=1, max_length=200)
    target_audience: str = "покупатели Wildberries"
    tone: str = "продающий и информативный"
    apply_changes: bool = False


class CompetitorAnalyzeRequest(BaseModel):
    product_id: int
    competitors: list[dict] = Field(default_factory=list)


class PricingRequest(BaseModel):
    product_id: int
    target_margin_percent: float = Field(default=30, ge=0, le=95)
    current_price: float | None = Field(default=None, ge=0)
    cost_price: float | None = Field(default=None, ge=0)
    logistics_cost: float | None = Field(default=None, ge=0)
    commission_percent: float | None = Field(default=None, ge=0, le=100)
    ad_cost_per_unit: float | None = Field(default=None, ge=0)
    tax_percent: float = Field(default=6, ge=0, le=100)
    market_price: float | None = Field(default=None, ge=0)
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    save_inputs: bool = True

    @model_validator(mode="after")
    def validate_range(self):
        if self.min_price is not None and self.max_price is not None and self.min_price > self.max_price:
            raise ValueError("Минимальная цена не может быть выше максимальной")
        return self


class DemoAnalyticsRequest(BaseModel):
    product_ids: list[int] = Field(default_factory=list)


class RecommendationAction(BaseModel):
    action: str = Field(pattern="^(apply|dismiss)$")
