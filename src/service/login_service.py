from src.database import login
from src.database.database import async_session


async def user_login(uid: int) -> list:
    async with async_session() as session:
        return await login.user_login(session, uid)
