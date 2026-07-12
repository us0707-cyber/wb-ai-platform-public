from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String(20), default="admin", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    stores: Mapped[list["MarketplaceStore"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class MarketplaceStore(Base):
    __tablename__ = "marketplace_stores"
    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_owner_store_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(150))
    marketplace: Mapped[str] = mapped_column(String(50), default="wildberries")
    api_token: Mapped[str] = mapped_column(Text, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    connection_status: Mapped[str] = mapped_column(String(30), default="not_checked")
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str] = mapped_column(Text, default="")
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sync_status: Mapped[str] = mapped_column(String(30), default="never")
    sync_error: Mapped[str] = mapped_column(Text, default="")
    products_synced: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner: Mapped[User] = relationship(back_populates="stores")
    products: Mapped[list["Product"]] = relationship(back_populates="store", cascade="all, delete-orphan")

    @property
    def has_token(self) -> bool:
        return bool(self.api_token)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("marketplace_stores.id", ondelete="CASCADE"), index=True)
    nm_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    vendor_code: Mapped[str] = mapped_column(String(120), default="")
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(200), default="")
    brand: Mapped[str] = mapped_column(String(200), default="")
    price: Mapped[float] = mapped_column(Float, default=0)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[float] = mapped_column(Float, default=0)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0)
    discount: Mapped[float] = mapped_column(Float, default=0)
    cost_price: Mapped[float] = mapped_column(Float, default=0)
    commission_percent: Mapped[float] = mapped_column(Float, default=15)
    logistics_cost: Mapped[float] = mapped_column(Float, default=0)
    ad_spend_30d: Mapped[float] = mapped_column(Float, default=0)
    orders_30d: Mapped[int] = mapped_column(Integer, default=0)
    sales_30d: Mapped[int] = mapped_column(Integer, default=0)
    returns_30d: Mapped[int] = mapped_column(Integer, default=0)
    revenue_30d: Mapped[float] = mapped_column(Float, default=0)
    profit_30d: Mapped[float] = mapped_column(Float, default=0)
    ctr: Mapped[float] = mapped_column(Float, default=0)
    conversion_rate: Mapped[float] = mapped_column(Float, default=0)
    competitor_avg_price: Mapped[float] = mapped_column(Float, default=0)
    recommended_price: Mapped[float] = mapped_column(Float, default=0)
    seo_score: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(30), default="draft", index=True)
    image_url: Mapped[str] = mapped_column(Text, default="")
    keywords: Mapped[list] = mapped_column(JSON, default=list)
    seo_title: Mapped[str] = mapped_column(String(500), default="")
    seo_description: Mapped[str] = mapped_column(Text, default="")
    seo_recommendations: Mapped[list] = mapped_column(JSON, default=list)
    seo_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    store: Mapped[MarketplaceStore] = relationship(back_populates="products")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    agent_type: Mapped[str] = mapped_column(String(80), index=True)
    input_data: Mapped[dict] = mapped_column(JSON, default=dict)
    output_data: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(30), default="completed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=True, index=True)
    kind: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(300))
    message: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(20), default="open", index=True)
    action_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    actor_username: Mapped[str] = mapped_column(String(100), default="system", index=True)
    action: Mapped[str] = mapped_column(String(100), index=True)
    entity_type: Mapped[str] = mapped_column(String(80), default="", index=True)
    entity_id: Mapped[str] = mapped_column(String(100), default="")
    status: Mapped[str] = mapped_column(String(20), default="success", index=True)
    request_id: Mapped[str] = mapped_column(String(64), default="", index=True)
    ip_address: Mapped[str] = mapped_column(String(64), default="")
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class AICache(Base):
    __tablename__ = "ai_cache"

    id: Mapped[int] = mapped_column(primary_key=True)
    cache_key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=True, index=True)
    task: Mapped[str] = mapped_column(String(80), index=True)
    provider: Mapped[str] = mapped_column(String(40), default="local")
    model: Mapped[str] = mapped_column(String(120), default="deterministic-v1")
    response_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class AnalyticsDaily(Base):
    __tablename__ = "analytics_daily"
    __table_args__ = (UniqueConstraint("product_id", "day", name="uq_analytics_product_day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    day: Mapped[date] = mapped_column(Date, index=True)
    orders: Mapped[int] = mapped_column(Integer, default=0)
    sales: Mapped[int] = mapped_column(Integer, default=0)
    returns: Mapped[int] = mapped_column(Integer, default=0)
    revenue: Mapped[float] = mapped_column(Float, default=0)
    profit: Mapped[float] = mapped_column(Float, default=0)
    ad_spend: Mapped[float] = mapped_column(Float, default=0)
    views: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    stock: Mapped[int] = mapped_column(Integer, default=0)
