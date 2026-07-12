from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import MarketplaceStore


class StoreRepository:
    """Persistence operations for marketplace stores.

    Business rules intentionally live in the service layer. This repository
    only knows how to query and persist Store entities.
    """

    def __init__(self, db: Session):
        self.db = db

    def list_for_owner(self, owner_id: int) -> list[MarketplaceStore]:
        query = (
            select(MarketplaceStore)
            .where(MarketplaceStore.owner_id == owner_id)
            .order_by(MarketplaceStore.id.desc())
        )
        return list(self.db.scalars(query))

    def get(self, store_id: int) -> MarketplaceStore | None:
        return self.db.get(MarketplaceStore, store_id)

    def get_for_owner(self, store_id: int, owner_id: int) -> MarketplaceStore | None:
        return self.db.scalar(
            select(MarketplaceStore).where(
                MarketplaceStore.id == store_id,
                MarketplaceStore.owner_id == owner_id,
            )
        )

    def find_by_name(self, owner_id: int, name: str) -> MarketplaceStore | None:
        return self.db.scalar(
            select(MarketplaceStore).where(
                MarketplaceStore.owner_id == owner_id,
                MarketplaceStore.name == name,
            )
        )

    def add(self, store: MarketplaceStore) -> MarketplaceStore:
        self.db.add(store)
        self.db.commit()
        self.db.refresh(store)
        return store

    def save(self, store: MarketplaceStore) -> MarketplaceStore:
        self.db.add(store)
        self.db.commit()
        self.db.refresh(store)
        return store

    def delete(self, store: MarketplaceStore) -> None:
        self.db.delete(store)
        self.db.commit()
