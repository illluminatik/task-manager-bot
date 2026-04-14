from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from core.models import User, Task, Priority
from datetime import datetime


async def get_or_create_user(session: AsyncSession, telegram_id: int, username: str | None) -> User:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


async def create_task(
    session: AsyncSession,
    user_id: int,
    title: str,
    description: str | None = None,
    priority: Priority = Priority.medium,
    deadline: datetime | None = None,
) -> Task:
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        priority=priority,
        deadline=deadline,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_user_tasks(
    session: AsyncSession,
    user_id: int,
    only_active: bool = False,
) -> list[Task]:
    query = select(Task).where(Task.user_id == user_id)
    if only_active:
        query = query.where(Task.is_done == False)
    query = query.order_by(Task.priority.desc(), Task.deadline)
    result = await session.execute(query)
    return result.scalars().all()


async def get_task_by_id(session: AsyncSession, task_id: int, user_id: int) -> Task | None:
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def mark_task_done(session: AsyncSession, task_id: int, user_id: int) -> Task | None:
    task = await get_task_by_id(session, task_id, user_id)
    if not task:
        return None
    task.is_done = True
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(session: AsyncSession, task_id: int, user_id: int) -> bool:
    task = await get_task_by_id(session, task_id, user_id)
    if not task:
        return False
    await session.delete(task)
    await session.commit()
    return True


async def get_overdue_tasks(session: AsyncSession) -> list[Task]:
    """Для планировщика напоминаний — все просроченные невыполненные задачи."""
    result = await session.execute(
        select(Task).where(
            Task.is_done == False,
            Task.deadline < datetime.utcnow(),
        )
    )
    return result.scalars().all()