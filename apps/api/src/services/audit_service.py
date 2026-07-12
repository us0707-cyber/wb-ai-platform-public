from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from src.models import AuditLog, User
from src.repositories.audit_repository import AuditRepository


def write_audit_log(
    db: Session,
    *,
    action: str,
    user: User | None = None,
    request: Request | None = None,
    entity_type: str = "",
    entity_id: int | str | None = None,
    status: str = "success",
    details: dict[str, Any] | None = None,
) -> AuditLog:
    request_id = ""
    ip_address = ""
    if request is not None:
        request_id = getattr(request.state, "request_id", "")
        if request.client:
            ip_address = request.client.host
    entry = AuditLog(
        user_id=user.id if user else None,
        actor_username=user.username if user else "anonymous",
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id or ""),
        status=status,
        request_id=request_id,
        ip_address=ip_address,
        details=details or {},
    )
    return AuditRepository(db).add(entry)
