from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models import Product
from src.repositories import ProductRepository, StoreRepository
from src.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, db: Session):
        self.products = ProductRepository(db)
        self.stores = StoreRepository(db)

    def list(self, owner_id: int, store_id: int | None = None) -> list[Product]:
        if store_id is not None and not self.stores.get_for_owner(store_id, owner_id):
            raise HTTPException(status_code=404, detail="Магазин не найден")
        return self.products.list_for_owner(owner_id, store_id)

    def get(self, product_id: int, owner_id: int) -> Product:
        product = self.products.get_for_owner(product_id, owner_id)
        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")
        return product

    def create(self, payload: ProductCreate, owner_id: int) -> Product:
        if not self.stores.get_for_owner(payload.store_id, owner_id):
            raise HTTPException(status_code=404, detail="Магазин не найден")
        return self.products.add(Product(**payload.model_dump()))

    def update(self, product_id: int, payload: ProductUpdate, owner_id: int) -> Product:
        product = self.get(product_id, owner_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(product, key, value)
        return self.products.save(product)

    def delete(self, product_id: int, owner_id: int) -> None:
        self.products.delete(self.get(product_id, owner_id))
