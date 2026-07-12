import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.session import Base
from src.models import Job, User
from src.schemas.jobs import JobCreate
from src.services.job_service import JobService


def make_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_create_and_list_job():
    db = make_db()
    user = User(email='a@example.com', username='a', hashed_password='x', role='admin')
    db.add(user)
    db.commit()
    db.refresh(user)

    service = JobService(db)
    job = service.create(user.id, JobCreate(type='system.noop', payload={'hello': 'world'}))
    items, total = service.list(user.id, status_value=None, limit=50, offset=0)

    assert job.status == 'pending'
    assert job.payload == {'hello': 'world'}
    assert total == 1
    assert items[0].id == job.id


def test_rejects_unknown_job_type():
    db = make_db()
    with pytest.raises(HTTPException) as exc:
        JobService(db).create(1, JobCreate(type='unknown.job'))
    assert exc.value.status_code == 422


def test_cancel_and_retry_job():
    db = make_db()
    user = User(email='b@example.com', username='b', hashed_password='x', role='admin')
    db.add(user)
    db.commit()
    db.refresh(user)
    service = JobService(db)
    job = service.create(user.id, JobCreate(type='system.noop'))

    cancelled = service.cancel(user.id, job.id)
    assert cancelled.status == 'cancelled'
    retried = service.retry(user.id, job.id)
    assert retried.status == 'pending'
