from sqlalchemy import func, select
from sqlalchemy.orm import Session
from src.models import AutopilotRule, MarketplaceStore, Product, Recommendation

class AutopilotRepository:
    def __init__(self, db: Session): self.db = db
    def create(self, item: AutopilotRule) -> AutopilotRule:
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def get_for_user(self, item_id: int, user_id: int) -> AutopilotRule | None:
        return self.db.scalar(select(AutopilotRule).where(AutopilotRule.id == item_id, AutopilotRule.user_id == user_id))
    def list_for_user(self, user_id: int, limit: int = 100, offset: int = 0):
        f=[AutopilotRule.user_id == user_id]
        q=select(AutopilotRule).where(*f).order_by(AutopilotRule.created_at.desc()).limit(limit).offset(offset)
        c=select(func.count()).select_from(AutopilotRule).where(*f)
        return list(self.db.scalars(q)), int(self.db.scalar(c) or 0)
    def enabled_for_user(self, user_id: int) -> list[AutopilotRule]:
        return list(self.db.scalars(select(AutopilotRule).where(AutopilotRule.user_id == user_id, AutopilotRule.enabled.is_(True))))
    def products_for_user(self, user_id: int) -> list[Product]:
        q=select(Product).join(MarketplaceStore).where(MarketplaceStore.owner_id == user_id)
        return list(self.db.scalars(q))
    def has_open_recommendation(self, user_id: int, product_id: int, kind: str) -> bool:
        q=select(Recommendation.id).where(Recommendation.user_id == user_id, Recommendation.product_id == product_id,
            Recommendation.kind == kind, Recommendation.status == "open")
        return self.db.scalar(q) is not None
    def add_recommendation(self, item: Recommendation) -> Recommendation:
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def save(self, item: AutopilotRule) -> AutopilotRule:
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def delete(self, item: AutopilotRule) -> None:
        self.db.delete(item); self.db.commit()
