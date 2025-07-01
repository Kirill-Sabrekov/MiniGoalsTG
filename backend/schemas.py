from pydantic import BaseModel
from datetime import datetime

class GoalCreate(BaseModel):
    title: str
    description: str | None = None
    deadline: datetime | None = None

class GoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    is_completed: bool | None = None

class GoalResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    deadline: datetime | None
    is_completed: bool
    created_at: datetime 