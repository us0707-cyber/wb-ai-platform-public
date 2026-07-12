from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import MarketplaceStore, Product


class ProductRepository:
    """Persistence operations for products with owner-scoped queries."""

    def __init__(self, db: Session):
        self.db = db

    def list_for_owner(self, owner_id: int, store_id: int | None = None) -> list[Product]:
        query = select(Product).join(MarketplaceStore).where(MarketplaceStore.owner_id == owner_id)
        if store_id is not None:
            query = query.where(Product.store_id == store_id)
        return list(self.db.scalars(query.order_by(Product.id.desc())))

    def get_for_owner(self, product_id: int, owner_id: int) -> Product | None:
        return self.db.scalar(
            select(Product)
            .join(MarketplaceStore)
            .where(Product.id == product_id, MarketplaceStore.owner_id == owner_id)
        )

    def add(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def save(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.commit()
