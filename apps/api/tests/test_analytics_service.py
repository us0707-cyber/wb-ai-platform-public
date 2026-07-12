from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.database.session import Base
from src.models import AnalyticsDaily, MarketplaceStore, Product, User
from src.services.analytics_service import AnalyticsService


def build_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def seed(db: Session):
    user = User(email="owner@example.com", username="owner", hashed_password="x", role="admin")
    db.add(user)
    db.flush()
    store = MarketplaceStore(owner_id=user.id, name="Store")
    db.add(store)
    db.flush()
    p1 = Product(store_id=store.id, title="A", price=1000, stock=10, revenue_30d=30000, sales_30d=30)
    p2 = Product(store_id=store.id, title="B", price=500, stock=100, revenue_30d=5000, sales_30d=10)
    db.add_all([p1, p2])
    db.commit()
    return user, p1, p2


def test_overview_fallback_uses_product_metrics():
    db = build_db()
    user, _, _ = seed(db)
    result = AnalyticsService(db).overview(user.id, 30)
    assert result["revenue"] == 35000
    assert result["sales"] == 40
    assert result["products_count"] == 2


def test_abc_xyz_orders_by_revenue():
    db = build_db()
    user, p1, p2 = seed(db)
    result = AnalyticsService(db).abc_xyz(user.id, 30)
    assert result[0]["product_id"] == p1.id
    assert result[0]["abc_class"] == "A"
    assert result[-1]["product_id"] == p2.id


def test_forecast_detects_low_stock():
    db = build_db()
    user, p1, _ = seed(db)
    today = date.today()
    for i in range(30):
        db.add(AnalyticsDaily(user_id=user.id, product_id=p1.id, day=today - timedelta(days=i), sales=2, revenue=2000))
    db.commit()
    result = AnalyticsService(db).forecast(user.id, 30)
    item = next(x for x in result if x["product_id"] == p1.id)
    assert item["forecast_sales_30d"] == 60
    assert item["days_of_stock"] == 5.0
    assert item["suggested_reorder"] > 0


def test_trends_returns_complete_date_range():
    db = build_db()
    user, _, _ = seed(db)
    result = AnalyticsService(db).trends(user.id, 7)
    assert len(result) == 7
    assert result[0]["day"] == date.today() - timedelta(days=6)
