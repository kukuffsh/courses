from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List
from src.database.models import models
from sqlalchemy import select, Sequence

from src.database.models.models import UserRow


async def get_users_by_ids(session: AsyncSession, teacher_ids: list[int]) -> list[UserRow]:
    result = await session.execute(
        select(UserRow).filter(UserRow.id.in_(teacher_ids))
    )
    return result.scalars().all()
