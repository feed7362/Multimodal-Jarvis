from sqlalchemy.sql.expression import select
from src.auth.models import UserSettings
from fastapi_users import models as fastapi_users_models
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
import gradio as gr
import uuid
from fastapi import Depends, FastAPI
from src.auth.schemas import UserRead, UserCreate
from src.auth.base_config import auth_backend, fastapi_users
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.pages.router import router_main as pages_router
from src.pages.router import router_login as login_router
from src.gradio_ui import create_chat_ui, create_setting_ui

app = FastAPI(
    title="JaRvis",
    description="ML project",
    version="0.0.1"
)
app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.include_router(pages_router)
app.include_router(login_router)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)

from pydantic import BaseModel
from typing import Optional

class MessagePayload(BaseModel):
    role: str
    content: str
    metadata: Optional[dict] = None


@app.post("/api/v1/agents/{agent_id}/sessions")
async def create_session(agent_id: str):
    return {"id": str(uuid.uuid4())}

@app.post("/api/v1/sessions/{session_id}/messages")
async def send_message(session_id: str, payload: MessagePayload):
    # Simulate LLM response
    return {"response": f"Bot reply to '{payload.content}'", "state": "ACTIVE"}


@app.get("/api/v1/user/settings")
async def get_user_settings(user: fastapi_users_models.BaseUserDB = Depends(fastapi_users.current_user()),
                            db: AsyncSession = Depends(get_async_session)):
    settings = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user.id)
    )
    user_settings = settings.scalar_one_or_none()
    return user_settings.settings if user_settings else {}

@app.post("/api/v1/user/settings")
async def update_user_settings(new_settings: dict,
                               user: fastapi_users_models.BaseUserDB = Depends(fastapi_users.current_user()),
                               db: AsyncSession = Depends(get_async_session)):
    settings = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user.id)
    )
    user_settings = settings.scalar_one_or_none()
    if user_settings:
        user_settings.settings = new_settings
    else:
        user_settings = UserSettings(user_id=user.id, settings=new_settings)
        db.add(user_settings)
    await db.commit()
    return {"message": "Settings updated"}

app = gr.mount_gradio_app(app, create_chat_ui(), path='/chat', show_error=True, max_file_size="50mb", show_api=False)
app = gr.mount_gradio_app(app, create_setting_ui(), path='/settings', show_error=True, max_file_size="50mb", show_api=False)