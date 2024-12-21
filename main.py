from fastapi import FastAPI
import uvicorn
from src.routers.course_router import courses_router
from src.routers.login_router import router
from src.database.database import engine
from src.database.models.models import Base

app = FastAPI()
app.include_router(courses_router)
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

