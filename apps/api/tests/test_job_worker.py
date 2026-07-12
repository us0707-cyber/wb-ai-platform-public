from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.session import Base
from src.jobs.worker import JobWorker
from src.models import Job, User
from src.repositories.job_repository import JobRepository


def test_noop_handler_shape():
    result = JobWorker._handle_noop(None, {'x': 1}, 1)
    assert result == {'ok': True, 'echo': {'x': 1}}
