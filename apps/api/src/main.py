import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from src.api.v1.router import api_router
from src.core.config import settings
from src.core.errors import install_exception_handlers
from src.core.logging import configure_logging
from src.database.session import engine
from src.middleware import RequestContextMiddleware
from src.jobs import JobWorker, SchedulerWorker

configure_logging()
logger = logging.getLogger(__name__)
job_worker = JobWorker()
scheduler_worker = SchedulerWorker()


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting %s in %s mode", settings.app_name, settings.app_env)
    job_worker.start()
    scheduler_worker.start()
    yield
    scheduler_worker.stop()
    job_worker.stop()
    logger.info("Stopping %s", settings.app_name)


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
install_exception_handlers(app)
app.include_router(api_router)
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")


@app.get("/health")
def health():
    result = {"api": "ok", "postgres": "error", "redis": "error"}
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        result["postgres"] = "ok"
    except Exception as exc:  # pragma: no cover - environment dependent
        logger.warning("Postgres health check failed: %s", exc)

    try:
        from redis import Redis
        client = Redis.from_url(settings.redis_url, socket_connect_timeout=2, socket_timeout=2)
        result["redis"] = "ok" if client.ping() else "error"
    except Exception as exc:  # pragma: no cover - environment dependent
        logger.warning("Redis health check failed: %s", exc)

    return result


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"app_name": settings.app_name})
