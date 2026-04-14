from fastapi import FastAPI
from api.routers import tasks
from core.database import init_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Task Manager API", lifespan=lifespan)
app.include_router(tasks.router)