from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from src.api.deps import get_current_user, require_min_role
from src.database.session import get_db
from src.models import User
from src.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from src.services.audit_service import write_audit_log
from src.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[ProductResponse])
def list_products(store_id: int | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ProductService(db).list(user.id, store_id)


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(payload: ProductCreate, request: Request, user: User = Depends(require_min_role("manager")), db: Session = Depends(get_db)):
    product = ProductService(db).create(payload, user.id)
    write_audit_log(db, action="product.create", user=user, request=request, entity_type="product", entity_id=product.id, details={"title": product.title})
    return product


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ProductService(db).get(product_id, user.id)


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, payload: ProductUpdate, request: Request, user: User = Depends(require_min_role("manager")), db: Session = Depends(get_db)):
    product = ProductService(db).update(product_id, payload, user.id)
    write_audit_log(db, action="product.update", user=user, request=request, entity_type="product", entity_id=product.id, details={"fields": list(payload.model_dump(exclude_unset=True))})
    return product


@router.delete("/{product_id}")
def delete_product(product_id: int, request: Request, user: User = Depends(require_min_role("admin")), db: Session = Depends(get_db)):
    product = ProductService(db).get(product_id, user.id)
    title = product.title
    ProductService(db).delete(product_id, user.id)
    write_audit_log(db, action="product.delete", user=user, request=request, entity_type="product", entity_id=product_id, details={"title": title})
    return {"ok": True}
