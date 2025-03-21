import uuid
from datetime import datetime
from typing import Optional, Dict, Any, Union
from fastapi import Depends, Request, Response
from fastapi_users import BaseUserManager, UUIDIDMixin, exceptions, models, schemas, InvalidPasswordException
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import UserCreate
from src.config import settings
from src.auth.models import User, UserSettings
from src.auth.crud import get_user_db
from src.database import get_async_session
from src.gradio_ui import load_default_preset


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID4]):
    reset_password_token_secret = settings.SECRET_AUTH
    verification_token_secret = settings.SECRET_AUTH

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.username} has registered.")

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email) 
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["role_id"] = uuid.UUID("e147083d-4e8e-4bd2-bb25-abd96d9e6e1c")
        async for session in get_async_session():
            user_dict["user_settings"] = uuid.UUID(await create_user_settings(session))
            
        created_user = await self.user_db.create(user_dict)
        
        await self.on_after_register(created_user, request)

        return created_user

    async def validate_password(
            self,
            password: str,
            user: Union[UserCreate, User],
    ) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail"
            )
    
    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def on_after_verify(
            self, user: User, request: Optional[Request] = None
    ):
        print(f"User {user.id} has been verified")
    async def on_after_login(
            self,
            user: User, 
            request: Optional[Request] = None,
            response: Optional[Response] = None,
    ):
        print(f"User {user.id} logged in.")

    async def on_before_delete(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} is going to be deleted")

    async def on_after_delete(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} is successfully deleted")

    async def on_after_update(
            self,
            user: User,
            update_dict: Dict[str, Any],
            request: Optional[Request] = None,
    ):
        print(f"User {user.id} has been updated with {update_dict}.")

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

async def create_user_settings(session: AsyncSession):
    new_settings = UserSettings(
        id=uuid.uuid4(),                       # Explicitly setting the id (optional, since default exists)
        settings=load_default_preset(),
        updated_at=datetime.now()       # Optional (onupdate already handles it)
    )

    session.add(new_settings)             # Add the object to the session
    await session.commit()                      # Commit the transaction
    await session.refresh(new_settings)
    print(f"New settings created with ID: {new_settings.id}")
    return str(new_settings.id)