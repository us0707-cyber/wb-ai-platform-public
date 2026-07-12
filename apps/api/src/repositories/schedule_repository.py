from datetime import datetime
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from src.models import Schedule

class ScheduleRepository:
    def __init__(self, db: Session): self.db = db
    def create(self, item: Schedule) -> Schedule:
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def get_for_user(self, item_id: int, user_id: int) -> Schedule | None:
        return self.db.scalar(select(Schedule).where(Schedule.id == item_id, Schedule.user_id == user_id))
    def list_for_user(self, user_id: int, limit: int = 100, offset: int = 0):
        f=[Schedule.user_id == user_id]
        q=select(Schedule).where(*f).order_by(Schedule.created_at.desc()).limit(limit).offset(offset)
        c=select(func.count()).select_from(Schedule).where(*f)
        return list(self.db.scalars(q)), int(self.db.scalar(c) or 0)
    def due(self, now: datetime, limit: int = 50) -> list[Schedule]:
        q=(select(Schedule).where(Schedule.enabled.is_(True), Schedule.next_run_at <= now)
           .order_by(Schedule.next_run_at.asc()).limit(limit))
        return list(self.db.scalars(q))
    def save(self, item: Schedule) -> Schedule:
        self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def delete(self, item: Schedule) -> None:
        self.db.delete(item); self.db.commit()
