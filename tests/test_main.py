import gradio as gr
import asyncio
from fastapi import FastAPI
from src.auth.schemas import UserRead, UserCreate
from src.auth.base_config import auth_backend, fastapi_users
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.pages.router import router_main as pages_router
from src.pages.router import router_login as login_router

custom_gradio_css = 'src/static/custom_gradio.css'

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


async def echo(message, history):
    try:
        history_output = [{"role": "assistant", "content": ""}]

        generated_text = f"You said: {message}"
        for char in generated_text :
            history_output[-1]["content"] += char
            await asyncio.sleep(0.01) 
            yield history_output
    except Exception as e:
        gr.Error(str(e), 15)

# async def echos(text, history, request: gr.Request):
#     if request:
#         print("Request headers dictionary:", request.headers)
#         print("IP address:", request.client.host)
#         print("Query parameters:", dict(request.query_params))
#         print("Session hash:", request.session_hash)
#     yield text
from src.database import async_engine
from fastapi import HTTPException
from sqlalchemy import text

@app.get("/db")
async def test_connection():
    try:
        async with async_engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
            return {"status": "success", "message": "Database connection successful!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "Database error",
            "data": str(e).capitalize(),
            "details": "Error connecting to database"
        })


def create_chat_ui():
    chat = gr.Chatbot( 
          height=600,
          min_width=800,
          type="messages",
          bubble_full_width=False,
          placeholder=f"<strong><br><big>JARvis</br></strong>",
          editable=True,
          show_share_button=False
      )
    textbox = gr.MultimodalTextbox(
          interactive=True,
          file_count="multiple",
          placeholder="Ask me a question",
          container=False,
          scale=7,
          show_label=False,
          sources=["microphone", "upload"],
      )
    with gr.Blocks(css_paths=custom_gradio_css) as blocks:
      with gr.Column(elem_classes=["footer"], show_progress=True):
        gr.ChatInterface(
          fn = echo,
          type='messages',
          save_history = True,
          show_progress = 'full',
          api_name = "chat_interface_api",
          analytics_enabled = True,
          textbox = textbox,
          chatbot = chat
        )
    return blocks

def create_setting_ui():
    with gr.Blocks(css_paths=custom_gradio_css) as blocks:
       with gr.Column(elem_classes=["footer"], show_progress=True):
        gr.Slider(minimum=0, maximum=100, label="Volume")
        gr.Slider(minimum=0, maximum=100, label="Brightness")
        gr.Slider(minimum=0, maximum=100, label="Contrast")

    return blocks


app = gr.mount_gradio_app(app, create_chat_ui(), path='/chat', show_error=True, max_file_size="50mb", show_api=False)
app = gr.mount_gradio_app(app, create_setting_ui(), path='/settings', show_error=True, max_file_size="50mb", show_api=False)
