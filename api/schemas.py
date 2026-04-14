from pydantic import BaseModel
from datetime import datetime
from core.models import Priority


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: Priority = Priority.medium
    deadline: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: Priority | None = None
    deadline: datetime | None = None
    is_done: bool | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    priority: Priority
    deadline: datetime | None
    is_done: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: str | None
    created_at: datetime

    model_config = {"from_attributes": True}