import json
from sqlalchemy.sql.expression import select

from src.auth.manager import get_user_manager
from src.auth.models import UserSettings
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
import gradio as gr
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from src.auth.schemas import UserRead, UserCreate, UserUpdate
from src.auth.base_config import auth_backend, fastapi_users, current_active_user, get_current_user, get_jwt_strategy
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from fastapi.staticfiles import StaticFiles
from src.pages.router import router_main as pages_router
from src.pages.router import router_login as login_router
from src.gradio_ui import create_chat_ui, create_setting_ui
from src.auth.models import User

from src.logger import CustomLogger
LOGGER = CustomLogger(__name__).logger

app = FastAPI(
    # lifespan="on",
    title="JaRvis",
    summary="App for ML project",
    description="ML project",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Deadpoolio the Amazing",
        "url": "http://x-force.example.com/contact/",
        "email": "dp@x-force.example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    redoc_url=None
)

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    LOGGER.info("Scalar API reference requested")
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
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
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate, requires_verification=True),
    prefix="/auth",
    tags=["users"],
)
# app.include_router(
#     fastapi_users.get_oauth_router(UserRead, UserCreate),
#     prefix="/auth",
#     tags=["auth"],
# )

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

app = gr.mount_gradio_app(app, create_chat_ui(), path='/chat', show_error=True, max_file_size="50mb", show_api=False, auth_dependency=get_current_user)
app = gr.mount_gradio_app(app, create_setting_ui(), path='/settings', show_error=True, max_file_size="3mb", show_api=False, auth_dependency=get_current_user)

# @app.post("/api/v1/sessions/{session_id}/messages")
# async def send_message(session_id: str, payload: MessagePayload):
#     # Simulate LLM response
#     return {"response": f"Bot reply to '{payload.content}'", "state": "ACTIVE"}


@app.get("/api/v1/user/settings", tags=["settings"])
async def get_user_settings(user: User = Depends(current_active_user),  db: AsyncSession = Depends(get_async_session)):
    settings = await db.execute(
        select(UserSettings).where(UserSettings.id == user.user_settings)
    )
    user_settings = settings.scalars().first()
    LOGGER.info("User settings (get /api/v1/user/settings) %s of %s user", user_settings, user.id)
    return user_settings.settings if user_settings else {}

@app.put("/api/v1/user/settings", tags=["settings"])
async def update_user_settings(new_settings: dict,
                               user: User = Depends(current_active_user),
                               db: AsyncSession = Depends(get_async_session)):
    LOGGER.debug("Updating settings for user %s", user.id)
    settings = await db.execute(
        select(UserSettings).where(UserSettings.id == user.user_settings)
    )
    user_settings = settings.scalars().first()
    if user_settings:
        user_settings.settings = new_settings
        LOGGER.info("Existing user settings found for user %s", user.id)
    else:
        user_settings = UserSettings(id=user.user_settings, settings=new_settings)
        db.add(user_settings)
        await db.flush()
        LOGGER.warning("User settings not found for user %s, creating new settings", user.id)
    await db.commit()
    await db.refresh(user_settings)
    LOGGER.info("User settings (put /api/v1/user/settings) %s of %s user", user_settings, user.id)
    return user_settings.settings

@app.get("/api/v1/protected-route")
async def protected_route(user: User = Depends(current_active_user)):
    return {"message": "Authenticated", "user": user.username}

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    @staticmethod
    async def send_personal_message(message: json, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws_sendMessages")
async def websocket_endpoint(websocket: WebSocket, db = Depends(get_user_manager)):
    user = await get_user_from_ws(websocket, db)
    if user is None:
        await websocket.close(code=1008)
        LOGGER.warning("Unauthorized WebSocket connection")
        return None
    try:
        await manager.connect(websocket, user.id)
        while True:
            data = await websocket.receive_json()

            await manager.send_personal_message({"response": f"Bot reply to '{data['content']}'", "state": "ACTIVE"}, websocket)
            await manager.broadcast(f"Client #{user.id} says: {data}")
            LOGGER.info("Client #%s says: %s", user.id, data)
    except WebSocketDisconnect:
        manager.disconnect(user.id)
        await manager.broadcast(f"Client #{user.id} left the chat")
        LOGGER.info("Client #%s left the chat", user.id)
    except Exception as e:
        LOGGER.error("Error during websocket connection: %s", e)
        return {"error": str(e)}

async def get_user_from_ws(websocket: WebSocket, user_db):
    token = websocket.cookies.get("bonds")
    LOGGER.debug("Token from WebSocket: %s", token)
    if token:
        try:
            payload = await get_jwt_strategy().read_token(token, user_db)
            LOGGER.info("Payload from WebSocket: %s", payload)
            if isinstance(payload, User):
                user = payload
            else:
                user = await user_db.get(payload["sub"])
            if user:
                LOGGER.info("User from WebSocket: %s", user)
                return user
        except Exception as e:
            LOGGER.error(f"Error authenticating user: {e}")
            await websocket.close(code=1008)
            raise Exception("Unauthorized WebSocket connection")
        
        
# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     response.headers["X-Process-Time"] = str(process_time)
#     return response