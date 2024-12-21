from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from src.database.database import async_session
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
async def create_user(id: int, email: str, role: str):
    async with async_session() as db:
        existing_user = await db.execute(select(models.UserRow).filter_by(email=email))
        if existing_user.scalars().first():
            raise HTTPException(status_code=400, detail="Email already registered")

        new_user = models.UserRow(id=id, email=email, role=role)
        db.add(new_user)

    await db.commit()

    return {"id": new_user.id, "email": new_user.email, "role": new_user.role}
