from datetime import date

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.models import AnalyticsDaily, MarketplaceStore, Product


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def products_for_user(self, user_id: int) -> list[Product]:
        return list(
            self.db.scalars(
                select(Product)
                .join(MarketplaceStore)
                .where(MarketplaceStore.owner_id == user_id)
                .order_by(Product.revenue_30d.desc(), Product.id)
            )
        )

    def facts(self, user_id: int, start: date, end: date) -> list[AnalyticsDaily]:
        return list(
            self.db.scalars(
                select(AnalyticsDaily)
                .where(
                    AnalyticsDaily.user_id == user_id,
                    AnalyticsDaily.day >= start,
                    AnalyticsDaily.day <= end,
                )
                .order_by(AnalyticsDaily.day, AnalyticsDaily.product_id)
            )
        )

    def replace_demo_facts(self, user_id: int, facts: list[AnalyticsDaily]) -> None:
        product_ids = sorted({fact.product_id for fact in facts})
        if product_ids:
            self.db.execute(
                delete(AnalyticsDaily).where(
                    AnalyticsDaily.user_id == user_id,
                    AnalyticsDaily.product_id.in_(product_ids),
                )
            )
        self.db.add_all(facts)
        self.db.commit()
