from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from fastapi_users.authentication import JWTStrategy
from fastapi.responses import JSONResponse
from pydantic import UUID4
from fastapi import Response, status
from src.auth.manager import get_user_manager
from src.auth.models import User
from src.config import settings

class CustomCookieTransport(CookieTransport):
    
    async def get_login_response(self, token: str) -> JSONResponse:
        response = JSONResponse(
            content={"access_token": token, "token_type": "bearer"},
            status_code=status.HTTP_200_OK,
        )
        return self._set_login_cookie(response, token)

    
cookie_transport = CustomCookieTransport(cookie_name="bonds", cookie_max_age=3600)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_AUTH, lifetime_seconds=3600)

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

current_user = fastapi_users.current_user()