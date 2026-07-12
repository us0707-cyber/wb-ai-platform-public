from __future__ import annotations

import logging
import threading
import time
from typing import Callable

from src.core.config import settings
from src.database.session import SessionLocal
from src.repositories.job_repository import JobRepository
from src.services.analytics_service import AnalyticsService
from src.services.autopilot_service import AutopilotService

logger = logging.getLogger(__name__)


class JobWorker:
    def __init__(self, poll_seconds: float | None = None):
        self.poll_seconds = poll_seconds or settings.job_worker_poll_seconds
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.handlers: dict[str, Callable] = {
            "system.noop": self._handle_noop,
            "analytics.seed_demo": self._handle_analytics_seed_demo,
            "autopilot.evaluate": self._handle_autopilot_evaluate,
        }

    def start(self) -> None:
        if not settings.job_worker_enabled or (self._thread and self._thread.is_alive()):
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="job-worker", daemon=True)
        self._thread.start()
        logger.info("Job worker started")

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Job worker stopped")

    def _run(self) -> None:
        while not self._stop.is_set():
            processed = self.run_once()
            if not processed:
                self._stop.wait(self.poll_seconds)

    def run_once(self) -> bool:
        db = SessionLocal()
        try:
            repo = JobRepository(db)
            job = repo.next_pending()
            if not job:
                return False
            repo.mark_running(job)
            handler = self.handlers.get(job.type)
            if not handler:
                repo.mark_failed(job, f"No handler registered for {job.type}")
                return True
            try:
                result = handler(db, job.payload, job.user_id)
                if job.status != "cancelled":
                    repo.mark_success(job, result or {})
            except Exception as exc:  # pragma: no cover - defensive path
                logger.exception("Job %s failed", job.id)
                repo.mark_failed(job, str(exc))
            return True
        finally:
            db.close()

    @staticmethod
    def _handle_noop(_db, payload: dict, _user_id: int) -> dict:
        return {"ok": True, "echo": payload}

    @staticmethod
    def _handle_analytics_seed_demo(db, payload: dict, user_id: int) -> dict:
        days = int(payload.get("days", 60))
        if not 30 <= days <= 365:
            raise ValueError("days must be between 30 and 365")
        created = AnalyticsService(db).seed_demo(user_id, days)
        return {"ok": True, "created": created, "days": days}

    @staticmethod
    def _handle_autopilot_evaluate(db, _payload: dict, user_id: int) -> dict:
        return {"ok": True, **AutopilotService(db).evaluate(user_id)}
