from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator
from sqlalchemy.ext.declarative import declarative_base
from src.config import settings
from sqlalchemy import MetaData

from src.logger import CustomLogger
LOGGER = CustomLogger(__name__).logger

DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
async_engine = create_async_engine(DATABASE_URL, echo=True)
LOGGER.info("Database connection established")
metadata = MetaData()

Base = declarative_base(metadata=metadata)

async_session_maker = async_sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)
LOGGER.info("Async session maker created")
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        LOGGER.info("Async session created")
        yield session