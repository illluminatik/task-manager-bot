from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.models import Base
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@127.0.0.1:5433/taskdb")

engine = create_async_engine(
    DATABASE_URL, 
    echo=True,
    connect_args={"server_settings": {"jit": "off"}}
)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session