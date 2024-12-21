from fastapi import APIRouter, HTTPException
from src.service.login_service import user_login
from src.auth.handler_auth import signJWT


router = APIRouter(tags=['Auth'])

@router.post("/login")
async def login(uid: int):
    user = await user_login(uid)
    if user:
        return signJWT(user[0], user[1])
    raise HTTPException(status_code=404, detail="Item Not Found")