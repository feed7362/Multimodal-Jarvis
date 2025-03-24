from fastapi import Depends,Request
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from fastapi_users.authentication import JWTStrategy
from pydantic import UUID4
from src.auth.manager import get_user_manager
from src.auth.models import User
from src.config import settings
import asyncio


cookie_transport = CookieTransport(cookie_name="bonds", 
                                   cookie_max_age=36000, # 10 hours
                                   cookie_secure=False)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_AUTH, lifetime_seconds=36000) # 10 hours

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, UUID4](
    get_user_manager,
    [auth_backend],
)
current_active_user = fastapi_users.current_user(active=True)

async def get_current_user_async(user=Depends(current_active_user)):
    return user

def get_current_user(request: Request):
    """Sync wrapper that calls the async function"""
    return asyncio.run(get_current_user_async(request))