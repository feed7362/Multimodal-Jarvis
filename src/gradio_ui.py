import uuid
from src.model import __audiofile_to_text__
import websockets
import json
import gradio as gr
import httpx

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(r"Q:\Projects\Multimodal-Jarvis\data\logs\app.log"),  # Save logs to a file
    ]
)

logging.info("Logging is set up!")
logger = logging.getLogger(__name__)

__GRADIO_CSS__ = 'src/static/custom_gradio.css'
BASE_URL = '127.0.0.1:8000'
AGENT_ID = 'chat'
HEADERS = {'Content-Type': 'application/json'}

async def send_message(session_id, message):
    url = f"ws://{BASE_URL}/ws_sendMessages"
    payload = {"role": "user",
               "content": message,
               "metadata": "None"}
    try:
        async with websockets.connect(url) as websocket:
            await websocket.send(json.dumps(payload))
            response = await websocket.recv()
        return json.loads(response)
    except Exception as exc:
        return {"error": str(exc)}


theme = gr.themes.Default(
    font=['Noto Sans', 'Helvetica', 'ui-sans-serif', 'system-ui', 'sans-serif'],
    font_mono=['IBM Plex Mono', 'ui-monospace', 'Consolas', 'monospace'],
).set(
    border_color_primary='#c5c5d2',
    button_large_padding='6px 12px',
    body_text_color_subdued='#484848',
    background_fill_secondary='#eaeaea',
    background_fill_primary='var(--neutral-50)',
    body_background_fill="white",
    block_background_fill="#f4f4f4",
    body_text_color="#333",
    button_secondary_background_fill="#f4f4f4",
    button_secondary_border_color="var(--border-color-primary)"
)


async def __add_message__(message, history, state):  # {'text': '123', 'files': []}
    try:
        if "session_id" not in state:
            state["session_id"] = f"id: {str(uuid.uuid4())}"  # Create a new session if it doesn't exist

        if message is not None:
            session_id = state.get("session_id")
            history.append({"role": "user", "content": message["text"]})

        if message and len(message["files"]) > 0:
            for file_path in message["files"]:
                if file_path.endswith(".wav"):
                    transcribed_text = await __audiofile_to_text__(file_path)
                    history.append({"role": "user", "content": file_path, "metadata": {"title": "🎤 User audio"}})
                    history.append({"role": "user", "content": transcribed_text})

        response_data = await send_message(session_id, history[-1]["content"])
        print(response_data)
        bot_reply = response_data.get("response", "No response")
        history.append({"role": "assistant", "content": bot_reply})

        state["history"] = history
        print(state)
        if response_data.get("state") == "WAITING_FOR_CONFIRMATION":
            yield bot_reply, state

        yield bot_reply, state

    except Exception as e:
        raise gr.Error(f"Unsupported Error: {str(e)}")


def create_chat_ui():
    with gr.Blocks(css_paths=__GRADIO_CSS__) as blocks:
        with gr.Column(elem_classes=["footer"], show_progress=True):
            state = gr.State({})
            chat = gr.Chatbot(
                height=600,
                type="messages",
                bubble_full_width=False,
                placeholder=f"<strong><br><big>JARvis</br></strong>",
                editable='user',
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
            gr.ChatInterface(
                editable=True,
                autoscroll=False,
                fn=__add_message__,
                additional_inputs=[state],
                additional_outputs=[state],
                type="messages",
                chatbot=chat,
                textbox=textbox,
                save_history=True,
                theme=theme,
                flagging_mode="manual",
                flagging_options=["Like", "Spam", "Inappropriate", "Other"],
            )

            return blocks

def create_setting_ui():
    with gr.Blocks(css_paths=__GRADIO_CSS__, elem_classes=["footer"]) as blocks:
        with gr.Column():
            temp = gr.Slider(0.0, 2.0, value=0.6, step=0.1, label="temp", interactive=True)
            top_k = gr.Slider(20, 1000, value=50, step=1, label="top_k", interactive=True)
            rep_penalty = gr.Slider(0.0, 2.0, value=1.0, step=0.1, label="rep_penalty", interactive=True)
            new_tokens = gr.Slider(64, 8192, value=1024, step=1, label="new_tokens", interactive=True)
            sample = gr.Radio([True, False], value=False, label="sample", interactive=True)
            with gr.Column():
                with gr.Row(elem_classes=["update-button"]):
                    button_update = gr.Button("Update", size="md", variant="primary")

            button_update.click(
                fn=put_settings,
                inputs=[temp, top_k, rep_penalty, new_tokens, sample],
                outputs=None,
                queue=False
            )
            
            blocks.load(
                fn=get_settings,
                inputs=None,
                outputs=[temp, top_k, rep_penalty, new_tokens, sample],
            )

    return blocks

def load_default_preset():
    return {
        'res_temp': 0.6,
        'res_topk': 50,
        'res_rpen': 1.0,
        'res_mnts': 1024,
        'res_sample': False
    }

async def get_settings(request : gr.Request):
    url = f"http://{BASE_URL}/api/v1/user/settings"
    cookies = request.cookies.get('bonds')
    headers = {'Content-Type': 'application/json', 'Cookie': f"bonds={cookies}"}
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, headers=headers)
    if response.status_code == 200:
        updated_settings = response.json()
        return (
            updated_settings["temp"],
            updated_settings["top_k"],
            updated_settings["rep_penalty"],
            updated_settings["new_tokens"],
            updated_settings["sample"],
        )  
    elif response.status_code == 401:
        raise gr.Error("Login to save settings")
    else:
        raise gr.Error(f"Failed to fetch settings: {response.status_code}")

async def put_settings(request: gr.Request, temp, top_k, rep_penalty, new_tokens, sample):
    params = {
        "temp": temp,
        "top_k": top_k,
        "rep_penalty": rep_penalty,
        "new_tokens": new_tokens,
        "sample": sample
    }
    url = f"http://{BASE_URL}/api/v1/user/settings"
    cookies = request.cookies.get('bonds')
    headers = {'Content-Type': 'application/json', 'Cookie': f"bonds={cookies}"}
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.put(url, headers=headers, json=params)
    if response.status_code == 200:
        return None
    if response.status_code == 401:
        raise gr.Error(f"Login to save settings")
    else:
        raise gr.Error(f"Failed to update settings: {response.status_code}")


