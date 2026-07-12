from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, model_validator

ScheduleType = Literal["once", "interval"]
Priority = Literal["low", "normal", "high", "critical"]

class ScheduleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    job_type: str = Field(min_length=2, max_length=80, pattern=r"^[a-z0-9_.-]+$")
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: Priority = "normal"
    schedule_type: ScheduleType = "interval"
    interval_minutes: int | None = Field(default=60, ge=1, le=525600)
    next_run_at: datetime
    enabled: bool = True

    @model_validator(mode="after")
    def validate_interval(self):
        if self.schedule_type == "interval" and self.interval_minutes is None:
            raise ValueError("interval_minutes is required for interval schedules")
        if self.schedule_type == "once":
            self.interval_minutes = None
        return self

class ScheduleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    payload: dict[str, Any] | None = None
    priority: Priority | None = None
    interval_minutes: int | None = Field(default=None, ge=1, le=525600)
    next_run_at: datetime | None = None
    enabled: bool | None = None

class ScheduleRead(BaseModel):
    id: int
    user_id: int
    name: str
    job_type: str
    payload: dict[str, Any]
    priority: Priority
    schedule_type: ScheduleType
    interval_minutes: int | None
    next_run_at: datetime
    last_run_at: datetime | None
    enabled: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

class ScheduleList(BaseModel):
    items: list[ScheduleRead]
    total: int
