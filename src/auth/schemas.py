import uuid
from fastapi_users import schemas
from pydantic import UUID4, EmailStr

class UserRead(schemas.BaseUser[UUID4]):
    id: UUID4
    email: EmailStr
    username: str
    role_id: UUID4
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True

class UserCreate(schemas.BaseUserCreate):
    username: str
    email: EmailStr
    password: str
    role_id: UUID4 = uuid.UUID('e147083d-4e8e-4bd2-bb25-abd96d9e6e1c')
    is_active: bool = True
    is_verified: bool = False

class UserUpdate(schemas.BaseUserUpdate):
    id: UUID4
    email: EmailStr
    username: str
    role_id: UUID4
    is_active: bool
    is_verified: bool

class UserLoginResponse(schemas.BaseOAuthAccount[UUID4]):
    access_token: str
    token_type: str = "bearer"
    username: str
    email: EmailStr
    is_active: bool
    is_verified: bool