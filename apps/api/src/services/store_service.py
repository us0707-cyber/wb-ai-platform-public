from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.integrations.wildberries import WildberriesClient
from src.models import MarketplaceStore
from src.repositories import StoreRepository
from src.schemas.store import StoreCreate, StoreUpdate
from src.services.token_service import decrypt_token, encrypt_token


def list_user_stores(db: Session, user_id: int) -> list[MarketplaceStore]:
    return StoreRepository(db).list_for_owner(user_id)


def get_user_store(db: Session, store_id: int, user_id: int) -> MarketplaceStore:
    store = StoreRepository(db).get_for_owner(store_id, user_id)
    if not store:
        raise HTTPException(status_code=404, detail="Магазин не найден")
    return store


def create_user_store(db: Session, user_id: int, payload: StoreCreate) -> MarketplaceStore:
    repository = StoreRepository(db)
    duplicate = repository.find_by_name(user_id, payload.name)
    if duplicate:
        raise HTTPException(status_code=409, detail="Магазин с таким названием уже существует")
    data = payload.model_dump()
    data["api_token"] = encrypt_token(data.get("api_token") or "")
    store = MarketplaceStore(owner_id=user_id, **data)
    return repository.add(store)


def update_user_store(db: Session, store: MarketplaceStore, payload: StoreUpdate) -> MarketplaceStore:
    data = payload.model_dump(exclude_unset=True)
    if "api_token" in data:
        data["api_token"] = encrypt_token(data["api_token"] or "")
        store.connection_status = "not_checked"
        store.last_error = ""
        store.last_checked_at = None
    for key, value in data.items():
        setattr(store, key, value)
    return StoreRepository(db).save(store)


async def check_user_store(db: Session, store: MarketplaceStore) -> dict:
    result = await WildberriesClient(decrypt_token(store.api_token)).ping()
    store.last_checked_at = datetime.utcnow()
    store.connection_status = "connected" if result.get("ok") else "error"
    store.last_error = "" if result.get("ok") else str(result.get("message", "Ошибка подключения"))[:1000]
    StoreRepository(db).save(store)
    return {**result, "store_id": store.id, "connection_status": store.connection_status}
