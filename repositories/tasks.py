from datetime import datetime
import logging
from typing import List, Optional

from loguru import logger
from db.tasks import tasks_model
from db.users import users_model
from models.task import Task, TaskIn
from repositories.base import BaseRepository
from pytz import timezone


class TaskRepository(BaseRepository):

    async def get_all(self, limit: int = 100, offset: int = 0) -> List:
        query = tasks_model.select().limit(limit).offset(offset)
        return await self.database.fetch_all(query)
    
    async def get_by_id(self, user_id: int) -> Optional[Task]:
        query = tasks_model.select().where(tasks_model.c.id == user_id).first()
        task = await self.database.fetch_one(query)
        if task is None:
            return None
        return Task.parse_obj(task)
    
    async def create(self, t: TaskIn) -> Task:
        task = Task(name=t.name, 
                    parent_task_id=t.parent_task_id,
                    assignee_id=t.assignee_id,
                    deadline=t.deadline,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow())
        
        values = {**task.dict()}
        values.pop("id", None)
        
        query = tasks_model.insert().values(**values)
        task.id = await self.database.execute(query)
        return task
    
    async def update(self, id: int, t: TaskIn) -> Task:
        task = Task(id=id,
                    name=t.name, 
                    parent_task_id=t.parent_task_id,
                    assignee_id=t.assignee_id,
                    deadline=t.deadline,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow())
        
        values = {**task.dict()}
        values.pop("id", None)
        values.pop("created_at", None)
        
        query = tasks_model.update().where(tasks_model.c.id==id).values(**values)
        task.id = await self.database.execute(query)
        return task

    async def delete(self, id: int):
        query = tasks_model.delete().where(tasks_model.c.id == id)
        await self.database.execute(query)
    
    
    async def get_important_tasks(self) -> List:
        ...
        
        
