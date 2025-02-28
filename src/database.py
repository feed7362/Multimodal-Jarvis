from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator
from sqlalchemy.ext.declarative import declarative_base
from src.config import settings
from sqlalchemy import MetaData

DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
async_engine = create_async_engine(DATABASE_URL, echo=True)

metadata = MetaData()

Base = declarative_base(metadata=metadata)

async_session_maker = async_sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# async def _init_db():
#     async with async_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     return {"ok": True}

async def test_connection():
    try:
        async with async_engine.connect() as connection:
            await connection.execute("SELECT 1")
            return "Database connection successful!"
    except Exception as e:
        return f"Error connecting to database: {e}"