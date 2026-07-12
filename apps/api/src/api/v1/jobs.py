from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_user, require_min_role
from src.database.session import get_db
from src.models import User
from src.schemas.jobs import JobCreate, JobList, JobRead
from src.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    user: User = Depends(require_min_role("manager")),
    db: Session = Depends(get_db),
):
    return JobService(db).create(user.id, payload)


@router.get("", response_model=JobList)
def list_jobs(
    status_value: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, total = JobService(db).list(user.id, status_value=status_value, limit=limit, offset=offset)
    return {"items": items, "total": total}


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return JobService(db).get(user.id, job_id)


@router.delete("/{job_id}", response_model=JobRead)
def cancel_job(
    job_id: int,
    user: User = Depends(require_min_role("manager")),
    db: Session = Depends(get_db),
):
    return JobService(db).cancel(user.id, job_id)


@router.post("/{job_id}/retry", response_model=JobRead)
def retry_job(
    job_id: int,
    user: User = Depends(require_min_role("manager")),
    db: Session = Depends(get_db),
):
    return JobService(db).retry(user.id, job_id)
