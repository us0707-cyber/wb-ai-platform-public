from datetime import datetime
from typing import Any

from src.schemas.common import ORMModel


class AuditLogResponse(ORMModel):
    id: int
    user_id: int | None
    actor_username: str
    action: str
    entity_type: str
    entity_id: str
    status: str
    request_id: str
    ip_address: str
    details: dict[str, Any]
    created_at: datetime
