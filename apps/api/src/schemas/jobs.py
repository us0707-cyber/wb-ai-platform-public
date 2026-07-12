from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

JobStatus = Literal["pending", "running", "success", "failed", "cancelled"]
JobPriority = Literal["low", "normal", "high", "critical"]


class JobCreate(BaseModel):
    type: str = Field(min_length=2, max_length=80, pattern=r"^[a-z0-9_.-]+$")
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: JobPriority = "normal"
    max_attempts: int = Field(default=3, ge=1, le=10)


class JobRead(BaseModel):
    id: int
    user_id: int
    type: str
    status: JobStatus
    priority: JobPriority
    payload: dict[str, Any]
    result: dict[str, Any]
    error: str
    attempts: int
    max_attempts: int
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    cancelled_at: datetime | None
    source_schedule_id: int | None

    model_config = {"from_attributes": True}


class JobList(BaseModel):
    items: list[JobRead]
    total: int
