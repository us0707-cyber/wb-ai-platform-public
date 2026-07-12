from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models import Job
from src.repositories.job_repository import JobRepository
from src.schemas.jobs import JobCreate

ALLOWED_JOB_TYPES = {
    "system.noop",
    "analytics.seed_demo",
    "autopilot.evaluate",
}


class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = JobRepository(db)

    def create(self, user_id: int, data: JobCreate) -> Job:
        if data.type not in ALLOWED_JOB_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unsupported job type: {data.type}",
            )
        return self.repo.create(
            Job(
                user_id=user_id,
                type=data.type,
                priority=data.priority,
                payload=data.payload,
                max_attempts=data.max_attempts,
            )
        )

    def get(self, user_id: int, job_id: int) -> Job:
        job = self.repo.get_for_user(job_id, user_id)
        if not job:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        return job

    def list(self, user_id: int, *, status_value: str | None, limit: int, offset: int):
        return self.repo.list_for_user(user_id, status=status_value, limit=limit, offset=offset)

    def cancel(self, user_id: int, job_id: int) -> Job:
        job = self.get(user_id, job_id)
        if job.status not in {"pending", "running"}:
            raise HTTPException(status_code=409, detail="Эту задачу уже нельзя отменить")
        return self.repo.cancel(job)

    def retry(self, user_id: int, job_id: int) -> Job:
        job = self.get(user_id, job_id)
        if job.status not in {"failed", "cancelled"}:
            raise HTTPException(status_code=409, detail="Повторный запуск доступен только для failed/cancelled")
        if job.attempts >= job.max_attempts:
            job.attempts = 0
        return self.repo.retry(job)
