from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from src.api.deps import get_current_user, require_min_role
from src.database.session import get_db
from src.models import User
from src.schemas.store import StoreCreate, StoreResponse, StoreUpdate
from src.services.audit_service import write_audit_log
from src.services.store_service import (
    check_user_store,
    create_user_store,
    get_user_store,
    list_user_stores,
    update_user_store,
)

router = APIRouter(prefix="/stores", tags=["Stores"])


@router.get("", response_model=list[StoreResponse])
def list_stores(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_user_stores(db, user.id)


@router.post("", response_model=StoreResponse, status_code=201)
def create_store(payload: StoreCreate, request: Request, user: User = Depends(require_min_role("manager")), db: Session = Depends(get_db)):
    store = create_user_store(db, user.id, payload)
    write_audit_log(db, action="store.create", user=user, request=request, entity_type="store", entity_id=store.id, details={"name": store.name})
    return store


@router.patch("/{store_id}", response_model=StoreResponse)
def update_store(store_id: int, payload: StoreUpdate, request: Request, user: User = Depends(require_min_role("manager")), db: Session = Depends(get_db)):
    store = update_user_store(db, get_user_store(db, store_id, user.id), payload)
    write_audit_log(db, action="store.update", user=user, request=request, entity_type="store", entity_id=store.id, details={"fields": list(payload.model_dump(exclude_unset=True))})
    return store


@router.delete("/{store_id}")
def delete_store(store_id: int, request: Request, user: User = Depends(require_min_role("admin")), db: Session = Depends(get_db)):
    store = get_user_store(db, store_id, user.id)
    from src.repositories import StoreRepository
    store_name = store.name
    StoreRepository(db).delete(store)
    write_audit_log(db, action="store.delete", user=user, request=request, entity_type="store", entity_id=store_id, details={"name": store_name})
    return {"ok": True}


@router.post("/{store_id}/check")
async def check_store(store_id: int, user: User = Depends(require_min_role("manager")), db: Session = Depends(get_db)):
    return await check_user_store(db, get_user_store(db, store_id, user.id))
