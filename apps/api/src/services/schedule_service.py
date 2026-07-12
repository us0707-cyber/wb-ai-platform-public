from datetime import UTC, datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models import Job, Schedule
from src.repositories.job_repository import JobRepository
from src.repositories.schedule_repository import ScheduleRepository
from src.schemas.schedules import ScheduleCreate, ScheduleUpdate
from src.services.job_service import ALLOWED_JOB_TYPES

def utcnow_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)

def normalize_datetime(value: datetime) -> datetime:
    return value.astimezone(UTC).replace(tzinfo=None) if value.tzinfo else value

class ScheduleService:
    def __init__(self, db: Session): self.db=db; self.repo=ScheduleRepository(db)
    def create(self, user_id: int, data: ScheduleCreate) -> Schedule:
        if data.job_type not in ALLOWED_JOB_TYPES:
            raise HTTPException(status_code=422, detail=f"Unsupported job type: {data.job_type}")
        return self.repo.create(Schedule(user_id=user_id, name=data.name, job_type=data.job_type,
            payload=data.payload, priority=data.priority, schedule_type=data.schedule_type,
            interval_minutes=data.interval_minutes, next_run_at=normalize_datetime(data.next_run_at), enabled=data.enabled))
    def get(self, user_id: int, item_id: int) -> Schedule:
        item=self.repo.get_for_user(item_id,user_id)
        if not item: raise HTTPException(status_code=404, detail="Расписание не найдено")
        return item
    def list(self,user_id:int,limit:int,offset:int): return self.repo.list_for_user(user_id,limit,offset)
    def update(self,user_id:int,item_id:int,data:ScheduleUpdate)->Schedule:
        item=self.get(user_id,item_id)
        for k,v in data.model_dump(exclude_unset=True).items():
            if k == "next_run_at" and v is not None: v=normalize_datetime(v)
            setattr(item,k,v)
        return self.repo.save(item)
    def delete(self,user_id:int,item_id:int)->None: self.repo.delete(self.get(user_id,item_id))
    def trigger(self,user_id:int,item_id:int)->Job:
        item=self.get(user_id,item_id)
        return JobRepository(self.db).create(Job(user_id=user_id,type=item.job_type,priority=item.priority,
            payload=item.payload,source_schedule_id=item.id))
    def enqueue_due(self, now: datetime | None = None) -> int:
        now=normalize_datetime(now or utcnow_naive()); count=0
        for item in self.repo.due(now):
            JobRepository(self.db).create(Job(user_id=item.user_id,type=item.job_type,priority=item.priority,
                payload=item.payload,source_schedule_id=item.id))
            item.last_run_at=now
            if item.schedule_type == "once": item.enabled=False
            else:
                base=max(item.next_run_at,now)
                item.next_run_at=base+timedelta(minutes=int(item.interval_minutes or 60))
            self.repo.save(item); count+=1
        return count
