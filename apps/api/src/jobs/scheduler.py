import logging, threading
from src.core.config import settings
from src.database.session import SessionLocal
from src.services.schedule_service import ScheduleService
logger=logging.getLogger(__name__)
class SchedulerWorker:
    def __init__(self,poll_seconds:float|None=None):
        self.poll_seconds=poll_seconds or settings.scheduler_poll_seconds; self._stop=threading.Event(); self._thread=None
    def start(self):
        if not settings.scheduler_enabled or (self._thread and self._thread.is_alive()): return
        self._stop.clear(); self._thread=threading.Thread(target=self._run,name="scheduler-worker",daemon=True); self._thread.start(); logger.info("Scheduler worker started")
    def stop(self):
        self._stop.set()
        if self._thread: self._thread.join(timeout=5)
        logger.info("Scheduler worker stopped")
    def _run(self):
        while not self._stop.is_set():
            self.run_once(); self._stop.wait(self.poll_seconds)
    def run_once(self)->int:
        db=SessionLocal()
        try: return ScheduleService(db).enqueue_due()
        except Exception: logger.exception("Scheduler tick failed"); return 0
        finally: db.close()
