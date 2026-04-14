from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_session
from core.crud import (
    create_task, get_user_tasks,
    get_task_by_id, mark_task_done, delete_task
)
from api.schemas import TaskCreate, TaskResponse
from api.dependencies import verify_api_token

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(verify_api_token)] # Теперь все ручки защищены!
)


@router.post("/{telegram_id}", response_model=TaskResponse)
async def add_task(
    telegram_id: int,
    data: TaskCreate,
    session: AsyncSession = Depends(get_session),
):
    from core.crud import get_or_create_user
    user = await get_or_create_user(session, telegram_id, None)
    task = await create_task(
        session,
        user_id=user.id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        deadline=data.deadline,
    )
    return task


@router.get("/{telegram_id}", response_model=list[TaskResponse])
async def list_tasks(
    telegram_id: int,
    only_active: bool = False,
    session: AsyncSession = Depends(get_session),
):
    from core.crud import get_or_create_user
    user = await get_or_create_user(session, telegram_id, None)
    tasks = await get_user_tasks(session, user.id, only_active)
    return tasks


@router.patch("/{telegram_id}/{task_id}/done", response_model=TaskResponse)
async def complete_task(
    telegram_id: int,
    task_id: int,
    session: AsyncSession = Depends(get_session),
):
    from core.crud import get_or_create_user
    user = await get_or_create_user(session, telegram_id, None)
    task = await mark_task_done(session, task_id, user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.delete("/{telegram_id}/{task_id}")
async def remove_task(
    telegram_id: int,
    task_id: int,
    session: AsyncSession = Depends(get_session),
):
    from core.crud import get_or_create_user
    user = await get_or_create_user(session, telegram_id, None)
    success = await delete_task(session, task_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return {"detail": "Задача удалена"}