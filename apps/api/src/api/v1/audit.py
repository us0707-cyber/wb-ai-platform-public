from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.database.session import get_db
from src.models import User
from src.repositories.audit_repository import AuditRepository
from src.schemas.audit import AuditLogResponse

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("", response_model=list[AuditLogResponse])
def list_audit_logs(
    limit: int = Query(default=100, ge=1, le=500),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repository = AuditRepository(db)
    if user.role == "admin":
        return repository.list_all(limit)
    return repository.list_for_user(user.id, limit)
