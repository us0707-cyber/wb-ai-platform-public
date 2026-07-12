from datetime import datetime, timedelta
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from src.database.session import Base
from src.models import Job, User
from src.schemas.schedules import ScheduleCreate
from src.services.schedule_service import ScheduleService

def make_db():
    e=create_engine("sqlite:///:memory:"); Base.metadata.create_all(e); return sessionmaker(bind=e)()
def test_due_interval_schedule_enqueues_job_and_moves_next_run():
    db=make_db(); u=User(email="s@x.com",username="s",hashed_password="x",role="admin"); db.add(u); db.commit(); db.refresh(u)
    now=datetime.utcnow(); svc=ScheduleService(db)
    item=svc.create(u.id,ScheduleCreate(name="demo",job_type="system.noop",next_run_at=now-timedelta(minutes=1),interval_minutes=30))
    assert svc.enqueue_due(now)==1
    job=db.scalar(select(Job)); db.refresh(item)
    assert job.source_schedule_id==item.id and item.last_run_at is not None and item.next_run_at>now

def test_once_schedule_disables_after_run():
    db=make_db(); u=User(email="o@x.com",username="o",hashed_password="x",role="admin"); db.add(u); db.commit(); db.refresh(u)
    svc=ScheduleService(db); item=svc.create(u.id,ScheduleCreate(name="once",job_type="system.noop",schedule_type="once",interval_minutes=None,next_run_at=datetime.utcnow()))
    svc.enqueue_due(datetime.utcnow()+timedelta(seconds=1)); db.refresh(item); assert item.enabled is False
