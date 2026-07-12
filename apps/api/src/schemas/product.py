from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from src.schemas.common import ORMModel

ALLOWED_PRODUCT_STATUSES = {"draft", "active", "archived"}


class ProductCreate(BaseModel):
    store_id: int = Field(gt=0)
    nm_id: int | None = Field(default=None, gt=0)
    vendor_code: str = Field(default="", max_length=120)
    title: str = Field(min_length=3, max_length=500)
    description: str = Field(default="", max_length=10000)
    category: str = Field(default="", max_length=200)
    brand: str = Field(default="", max_length=200)
    price: float = Field(default=0, ge=0)
    stock: int = Field(default=0, ge=0)
    rating: float = Field(default=0, ge=0, le=5)
    reviews_count: int = Field(default=0, ge=0)
    discount: float = Field(default=0, ge=0, le=100)
    cost_price: float = Field(default=0, ge=0)
    commission_percent: float = Field(default=15, ge=0, le=100)
    logistics_cost: float = Field(default=0, ge=0)
    ad_spend_30d: float = Field(default=0, ge=0)
    orders_30d: int = Field(default=0, ge=0)
    sales_30d: int = Field(default=0, ge=0)
    returns_30d: int = Field(default=0, ge=0)
    revenue_30d: float = Field(default=0, ge=0)
    ctr: float = Field(default=0, ge=0, le=100)
    conversion_rate: float = Field(default=0, ge=0, le=100)
    status: str = "draft"
    image_url: str = Field(default="", max_length=2000)

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in ALLOWED_PRODUCT_STATUSES:
            raise ValueError("Недопустимый статус товара")
        return value


class ProductUpdate(BaseModel):
    nm_id: int | None = Field(default=None, gt=0)
    vendor_code: str | None = Field(default=None, max_length=120)
    title: str | None = Field(default=None, min_length=3, max_length=500)
    description: str | None = Field(default=None, max_length=10000)
    category: str | None = Field(default=None, max_length=200)
    brand: str | None = Field(default=None, max_length=200)
    price: float | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    rating: float | None = Field(default=None, ge=0, le=5)
    reviews_count: int | None = Field(default=None, ge=0)
    discount: float | None = Field(default=None, ge=0, le=100)
    cost_price: float | None = Field(default=None, ge=0)
    commission_percent: float | None = Field(default=None, ge=0, le=100)
    logistics_cost: float | None = Field(default=None, ge=0)
    ad_spend_30d: float | None = Field(default=None, ge=0)
    orders_30d: int | None = Field(default=None, ge=0)
    sales_30d: int | None = Field(default=None, ge=0)
    returns_30d: int | None = Field(default=None, ge=0)
    revenue_30d: float | None = Field(default=None, ge=0)
    ctr: float | None = Field(default=None, ge=0, le=100)
    conversion_rate: float | None = Field(default=None, ge=0, le=100)
    status: str | None = None
    image_url: str | None = Field(default=None, max_length=2000)
    keywords: list[str] | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is not None and value not in ALLOWED_PRODUCT_STATUSES:
            raise ValueError("Недопустимый статус товара")
        return value


class ProductResponse(ORMModel):
    id: int
    store_id: int
    nm_id: int | None
    vendor_code: str
    title: str
    description: str
    category: str
    brand: str
    price: float
    stock: int
    rating: float
    reviews_count: int
    discount: float
    cost_price: float
    commission_percent: float
    logistics_cost: float
    ad_spend_30d: float
    orders_30d: int
    sales_30d: int
    returns_30d: int
    revenue_30d: float
    profit_30d: float
    ctr: float
    conversion_rate: float
    competitor_avg_price: float
    recommended_price: float
    seo_score: float
    status: str
    image_url: str
    keywords: list
    seo_title: str
    seo_description: str
    seo_recommendations: list
    seo_updated_at: datetime | None
