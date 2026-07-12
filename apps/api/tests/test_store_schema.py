from datetime import datetime

from src.schemas.store import StoreCreate, StoreResponse


class StoreObject:
    id = 1
    name = "Основной магазин"
    marketplace = "wildberries"
    is_active = True
    connection_status = "not_checked"
    last_checked_at = None
    last_error = ""
    has_token = True


def test_store_response_does_not_expose_token():
    payload = StoreResponse.model_validate(StoreObject()).model_dump()
    assert payload["has_token"] is True
    assert "api_token" not in payload


def test_store_create_accepts_null_token():
    payload = StoreCreate(name="Тестовый магазин", api_token=None)
    assert payload.api_token is None


def test_store_create_defaults_token_to_none():
    payload = StoreCreate(name="Тестовый магазин")
    assert payload.api_token is None
