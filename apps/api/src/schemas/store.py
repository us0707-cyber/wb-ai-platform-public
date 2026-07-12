from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.common import ORMModel


class StoreCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    api_token: str | None = None
    marketplace: str = "wildberries"


class StoreUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    api_token: str | None = None
    is_active: bool | None = None


class StoreResponse(ORMModel):
    id: int
    name: str
    marketplace: str
    is_active: bool
    connection_status: str
    last_checked_at: datetime | None
    last_error: str
    has_token: bool
    last_sync_at: datetime | None = None
    sync_status: str = "never"
    sync_error: str = ""
    products_synced: int = 0
