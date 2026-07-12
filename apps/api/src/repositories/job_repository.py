from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models import Job


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, job: Job) -> Job:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_for_user(self, job_id: int, user_id: int) -> Job | None:
        stmt = select(Job).where(Job.id == job_id, Job.user_id == user_id)
        return self.db.scalar(stmt)

    def list_for_user(self, user_id: int, *, status: str | None = None, limit: int = 50, offset: int = 0):
        filters = [Job.user_id == user_id]
        if status:
            filters.append(Job.status == status)
        stmt = select(Job).where(*filters).order_by(Job.created_at.desc()).limit(limit).offset(offset)
        count_stmt = select(func.count()).select_from(Job).where(*filters)
        return list(self.db.scalars(stmt)), int(self.db.scalar(count_stmt) or 0)

    def next_pending(self) -> Job | None:
        priority_order = {"critical": 4, "high": 3, "normal": 2, "low": 1}
        jobs = list(
            self.db.scalars(
                select(Job)
                .where(Job.status == "pending")
                .order_by(Job.created_at.asc())
                .limit(100)
            )
        )
        return max(jobs, key=lambda job: (priority_order.get(job.priority, 0), -job.id)) if jobs else None

    def mark_running(self, job: Job) -> Job:
        job.status = "running"
        job.started_at = datetime.now(UTC).replace(tzinfo=None)
        job.finished_at = None
        job.error = ""
        job.attempts += 1
        self.db.commit()
        self.db.refresh(job)
        return job

    def mark_success(self, job: Job, result: dict) -> Job:
        job.status = "success"
        job.result = result
        job.error = ""
        job.finished_at = datetime.now(UTC).replace(tzinfo=None)
        self.db.commit()
        self.db.refresh(job)
        return job

    def mark_failed(self, job: Job, error: str) -> Job:
        job.status = "failed" if job.attempts >= job.max_attempts else "pending"
        job.error = error[:4000]
        job.finished_at = datetime.now(UTC).replace(tzinfo=None) if job.status == "failed" else None
        self.db.commit()
        self.db.refresh(job)
        return job

    def cancel(self, job: Job) -> Job:
        job.status = "cancelled"
        job.cancelled_at = datetime.now(UTC).replace(tzinfo=None)
        job.finished_at = datetime.now(UTC).replace(tzinfo=None)
        self.db.commit()
        self.db.refresh(job)
        return job

    def retry(self, job: Job) -> Job:
        job.status = "pending"
        job.error = ""
        job.result = {}
        job.started_at = None
        job.finished_at = None
        job.cancelled_at = None
        self.db.commit()
        self.db.refresh(job)
        return job
