from repositories.users import UserRepository
from repositories.tasks import TaskRepository
from db.base import database


def get_user_repository() -> UserRepository:
    return UserRepository(database)


def get_task_repository() -> TaskRepository:
    return TaskRepository(database)
