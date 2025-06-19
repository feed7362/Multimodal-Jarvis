import uuid
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator
from sqlalchemy.ext.declarative import declarative_base
from src.config import database_settings as settings
from sqlalchemy import MetaData, select

from src.logger import CustomLogger
LOGGER = CustomLogger(__name__)

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASS}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_NAME}"
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

@asynccontextmanager
async def acquire_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def fetch_roles():
    from src.auth.models import Role
    roles = ["user", "admin"]
    async with acquire_session() as session:
        for name in roles:
            exists = await session.scalar(
                select(Role).where(Role.name == name).limit(1)
            )
            if not exists:
                session.add(Role(id=uuid.uuid4(), name=name, permissions={}))
        await session.commit()
    LOGGER.info("Roles created or verified.")

async def get_roles() -> dict[str, str]:
    from src.auth.models import Role
    async with acquire_session() as session:
        result = await session.execute(select(Role.id, Role.name))
        return {name: str(id_) for id_, name in result.all()}