from datetime import date

from pydantic import BaseModel, Field


class AnalyticsRange(BaseModel):
    days: int = Field(default=30, ge=7, le=365)


class AnalyticsPoint(BaseModel):
    day: date
    revenue: float
    profit: float
    orders: int
    sales: int
    ad_spend: float


class AnalyticsOverview(BaseModel):
    revenue: float
    profit: float
    orders: int
    sales: int
    returns: int
    ad_spend: float
    margin_percent: float
    romi_percent: float
    conversion_percent: float
    average_order_value: float
    stock_units: int
    products_count: int


class ABCXYZItem(BaseModel):
    product_id: int
    title: str
    revenue: float
    revenue_share_percent: float
    abc_class: str
    xyz_class: str
    coefficient_of_variation: float


class ForecastItem(BaseModel):
    product_id: int
    title: str
    average_daily_sales: float
    forecast_sales_7d: int
    forecast_sales_30d: int
    days_of_stock: float | None
    suggested_reorder: int
    confidence: str
