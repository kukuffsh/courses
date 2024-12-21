from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import user_dto
from src.service.login_service import user_login
from src.database.models import models
from src.auth.handler_auth import signJWT


router = APIRouter(tags=['Auth'])

@router.post("/login")
async def login(uid: int):
    user = await user_login(uid)
    if user:
        return signJWT(user[0], user[1])
    raise HTTPException(status_code=404, detail="Item Not Found")


@router.post("/register")
async def create_user(user: user_dto.UserCreate, db: AsyncSession):
    async with db.begin():
        existing_user = await db.execute(select(models.UserRow).filter_by(email=user.email))
        if existing_user.scalars().first():
            raise HTTPException(status_code=400, detail="Email already registered")

        new_user = models.UserRow(email=user.email, role=user.role)
        db.add(new_user)

    await db.commit()

    return {"id": new_user.id, "email": new_user.email, "role": new_user.role}