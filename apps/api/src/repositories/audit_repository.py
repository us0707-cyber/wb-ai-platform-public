from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import AuditLog


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, entry: AuditLog) -> AuditLog:
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def list_for_user(self, user_id: int, limit: int = 100) -> list[AuditLog]:
        query = (
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.id.desc())
            .limit(limit)
        )
        return list(self.db.scalars(query))

    def list_all(self, limit: int = 100) -> list[AuditLog]:
        query = select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)
        return list(self.db.scalars(query))
