from datetime import datetime
from typing import Optional
from pydantic import BaseModel, constr


class Task(BaseModel):
    id: Optional[int] = None
    name: str
    parent_task_id: Optional[int] = None
    assignee_id: int
    deadline: datetime
    created_at: datetime
    updated_at: datetime


class TaskIn(BaseModel):
    name: constr(min_length=8, max_length=32)  # type: ignore
    parent_task_id: Optional[int] = None
    assignee_id: int
    deadline: datetime

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "parent_task_id": 1,
                "assignee_id": 1,
                "deadline": "2023-05-13 17:35:07",
            }
        }
