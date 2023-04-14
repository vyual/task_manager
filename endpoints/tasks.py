from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from endpoints.depends import get_task_repository
from repositories.tasks import TaskRepository
from models.task import Task, TaskIn


router = APIRouter()

@router.get("/", response_model=List[Task], status_code=status.HTTP_200_OK)
async def read_tasks(
        task_repository: TaskRepository = Depends(get_task_repository),
        limit: int = 100, 
        offset: int = 0
    ):
    
    return await task_repository.get_all(limit, offset)


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
        task: TaskIn, 
        task_repository: TaskRepository = Depends(get_task_repository)
    ):
    return await task_repository.create(task)


@router.patch("/", response_model=Task, status_code=status.HTTP_202_ACCEPTED)
async def update_task(
        task_id: int, 
        task: TaskIn, 
        task_repository: TaskRepository = Depends(get_task_repository)):
    return await task_repository.update(task_id, task)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, task_repository: TaskRepository = Depends(get_task_repository)):
    return await task_repository.delete(task_id)


@router.get("/important_tasks", status_code=status.HTTP_200_OK)
async def read_important_tasks(task_repository: TaskRepository = Depends(get_task_repository)):
    return await task_repository.get_important_tasks()