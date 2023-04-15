from datetime import datetime
from typing import List, Optional

from loguru import logger
from sqlalchemy import text

from db.tasks import tasks_model
from models.task import Task, TaskIn
from repositories.base import BaseRepository


class TaskRepository(BaseRepository):

    async def get_all(self, limit: int = 100, offset: int = 0) -> List:
        query = tasks_model.select().limit(limit).offset(offset)
        return await self.database.fetch_all(query)

    async def get_by_id(self, task_id: int) -> Optional[Task]:
        query = tasks_model.select().where(tasks_model.c.id == task_id).limit(1)
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
        query = text(f"SELECT tasks.assignee_id, COUNT(tasks.id) as task_count "
                     f"FROM tasks "
                     f"WHERE tasks.completed = false AND tasks.assignee_id IS NOT NULL "
                     f"GROUP BY tasks.assignee_id "
                     f"ORDER BY task_count ASC "
                     f"LIMIT 1;")

        result = await self.database.fetch_one(query)
        if result is not None:
            """
            assignee_id, 
            task_count
            """
            return result

    async def get_potential_user_by_task(self, task_id: int):
        query = text(f'SELECT * FROM tasks WHERE id = {task_id};')
        task = await self.database.fetch_one(query)
        least_loaded_user = await self.get_least_loaded_user_by_tasks()

        if task is not None:
            if task["parent_task_id"] is not None:
                parent_task = await self.get_by_id(task["parent_task_id"])
                if parent_task is not None:
                    query = text(f'SELECT * FROM users WHERE id = {parent_task.assignee_id}')
                    user = await self.database.fetch_one(query)
                    if user is not None:
                        user_tasks_quantity_query = text(
                            f"SELECT COUNT(*) FROM tasks WHERE assignee_id = {user.id}")
                        user_tasks_quantity = await self.database.fetch_one(user_tasks_quantity_query)

                        if user_tasks_quantity["count"] <= least_loaded_user["task_count"] + 2:
                            return user["id"]
            else:
                return least_loaded_user

    async def get_important_tasks(self) -> List:
        query = text('SELECT * FROM tasks WHERE assignee_id IS NULL '
                     'AND completed = FALSE '
                     'AND parent_task_id IS NOT NULL;')
        return await self.database.fetch_all(query)

    async def get_potential_assignments(self) -> List:
        list_of_assignments = []
        task_list = await self.get_important_tasks()
        least_loaded_user = await self.get_least_loaded_user_by_tasks()

        logger.debug(
            f"least_loaded_user result: assignee id = {least_loaded_user[0]}, task_count = {least_loaded_user[1]}")
        logger.debug(f"task_list result: {task_list}")
        for task in task_list:
            potential_user = await self.get_potential_user_by_task(task["id"])

            logger.debug(f"task_list result: {task_list}")
            logger.debug(f"potential_user result: assignee id = {potential_user}")
            query = text(f'SELECT * FROM users WHERE id = {potential_user};')
            user = await self.database.fetch_one(query)
            logger.debug(f"user result: {user}")
            new_assignment = {"Важная задача": task.name, "ФИО": user.name,
                              "Срок": task.deadline.strftime("%d.%m.%Y %H:%M")}
            list_of_assignments.append(new_assignment)

        return list_of_assignments
