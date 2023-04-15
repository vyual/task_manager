from datetime import datetime
from typing import List, Optional

from loguru import logger
from db.tasks import tasks_model
from db.users import users_model
from models.task import Task, TaskIn
from models.user import User
from repositories.base import BaseRepository
from pytz import timezone
from sqlalchemy import select, func


class TaskRepository(BaseRepository):

    async def get_all(self, limit: int = 100, offset: int = 0) -> List:
        query = tasks_model.select().limit(limit).offset(offset)
        return await self.database.fetch_all(query)

    async def get_by_id(self, task_id: int) -> Optional[Task]:
        query = tasks_model.select().where(tasks_model.c.id == task_id).first()
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

        query = tasks_model.update().where(tasks_model.c.id == id).values(**values)
        task.id = await self.database.execute(query)
        return task

    async def delete(self, id: int):
        query = tasks_model.delete().where(tasks_model.c.id == id)
        await self.database.execute(query)

    async def get_parent_tasks(self) -> List:
        query = tasks_model.select().where(tasks_model.c.parent_task_id is not None)
        return await self.database.fetch_all(query)

    async def get_least_loaded_user_by_tasks(self):
        subquery = select([tasks_model.c.assignee_id, func.count().label('task_count')]).where(
            tasks_model.c.completed is False). \
            group_by(tasks_model.c.assignee_id).subquery()
        query = select([subquery.c.assignee_id]).order_by(subquery.c.task_count).limit(1)
        result = await self.database.fetch_one(query)
        if result is not None:
            return result[0]

    async def get_potential_user_by_task(self, task_id: int):
        query = tasks_model.select().where(tasks_model.c.id == task_id)
        task = await self.database.fetch_one(query)
        least_loaded_user = await self.get_least_loaded_user_by_tasks()
        if task is not None:
            if task["parent_task_id"] is not None:
                parent_task = await self.get_by_id(task["parent_task_id"])
                if parent_task is not None:
                    return parent_task.assignee_id
            else:
                return least_loaded_user

    async def get_important_tasks(self) -> List:
        query = tasks_model.select().where(tasks_model.c.assignee_id is None,
                                           tasks_model.c.completed is False,
                                           tasks_model.c.parent_task_id is not None)
        return await self.database.fetch_all(query)

    async def get_potential_assignments(self) -> List:
        list_of_assignments = []
        task_list = await self.get_important_tasks()
        for task in task_list:
            potential_user = await self.get_potential_user_by_task(task.c.id)
            query = users_model.select().where(users_model.c.id == potential_user).first()
            user = await self.database.fetch_one(query)
            user = User.parse_obj(user)
            new_assignment = {"Важная задача": task.c.name, "ФИО": user.name,
                              "Срок": task.c.deadline.strftime("%d.%m.%Y %H:%M")}
            list_of_assignments.append(new_assignment)

        return list_of_assignments
