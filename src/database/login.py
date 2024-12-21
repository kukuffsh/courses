from fastapi import HTTPException
from sqlalchemy import select
from src.database.models import models
from src.schemas import courses_dto
from src.database.database import async_session
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


async def user_login(session: AsyncSession, uid: int) -> list:
    query_course = select(models.UserRow).where(models.UserRow.id == uid)
    result_course = await session.execute(query_course)
    our_user = result_course.scalar_one_or_none()
    if not our_user:
        raise HTTPException(status_code=404, detail="Пользователя не существует!")
    return [our_user.id, our_user.role]