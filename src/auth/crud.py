from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.models import User
from src.database import get_async_session
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from src.logger import CustomLogger
LOGGER = CustomLogger(__name__).logger

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    LOGGER.info("Getting user database.", extra={"session": session})
    yield SQLAlchemyUserDatabase(session, User)
