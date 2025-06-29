from src.model import __audiofile_to_text__
import websockets
import json
import gradio as gr
import httpx
from src.i18n import _

from src.logger import CustomLogger
LOGGER = CustomLogger(__name__)

GRADIO_CSS = 'src/static/custom_gradio.css'
BASE_URL = '127.0.0.1:8000'
AGENT_ID = 'chat'
HEADERS = {'Content-Type': 'application/json'}


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


async def send_message(session_id: str, message: str, cookies: gr.Request):
    url = f"ws://{BASE_URL}/ws_sendMessages"
    headers = {'Cookie': f"{cookies}"}
    payload = {"role": "user", "content": message, "metadata": "None"}
    LOGGER.info("Sending message to the server with payload: %s", payload)
    try:
        async with websockets.connect(url, additional_headers=headers) as websocket:
            await websocket.send(json.dumps(payload))
            while True:
                try:
                    response = await websocket.recv()
                    LOGGER.info("Received response from the server: %s", response)
                    yield json.loads(response)
                except websockets.exceptions.ConnectionClosedOK:
                    LOGGER.info("Connection closed normally.")
                    break
                except Exception as e:
                    LOGGER.error("Stream error: %s", e)
                    break
            await websocket.close()
    except Exception as exc:
        LOGGER.error(f"Error during sending message: {str(exc)}")
        yield  {"Error while accepting message": str(exc)}


async def __add_message__(message: dict, history: list, state: dict, request: gr.Request):  # {'text': '123', 'files': []}
    try:
        if "session_id" not in state:
            state["session_id"] = request.session_hash
            LOGGER.info("New session created: %s", state["session_id"])

        if message is not None:
            session_id = state.get("session_id")
            history.append({"role": "user", "content": message["text"]})
            LOGGER.info("User message added to history: %s", message["text"])

        if message and len(message["files"]) > 0:
            for file_path in message["files"]:
                if file_path.endswith(".wav"):
                    transcribed_text = await __audiofile_to_text__(file_path)
                    history.append({"role": "user", "content": file_path, "metadata": {"title": "🎤 User audio"}})
                    history.append({"role": "user", "content": transcribed_text})
                    LOGGER.info("Transcribed audio file: %s -> %s", file_path, transcribed_text)

        prompt = history[-1]["content"]
        history.append({"role": "assistant", "content": " "})
        LOGGER.info("Prompt message added to history: %s", prompt)
        async for response_data in send_message(session_id, prompt, request.headers.get("cookie")):
            token = response_data.get("response", "No response")
            if isinstance(token, dict):
                if token.get("end_of_stream"):
                    LOGGER.info("Detected end_of_stream flag; finishing stream processing...")
                    break
            history[-1]["content"] += token
            
            yield history[-1]["content"], state

        state["history"] = history

    except Exception as e:
        LOGGER.error("Error in __add_message__: %s", str(e))
        raise gr.Error(f"Unsupported Error: {str(e)}")


def create_chat_ui():
    with gr.Blocks(css_paths=GRADIO_CSS) as blocks:
        with gr.Column(elem_classes=["footer"], show_progress=True):
            state = gr.State({})
            chat = gr.Chatbot(
                height=600,
                type="messages",
                bubble_full_width=False,
                placeholder=f"<strong><br><big>JARvis</br></strong>",
                editable='user',
                show_share_button=False,
                latex_delimiters=[
                    {'left': '$$', 'right': '$$', 'display': True},
                    {'left': '$', 'right': '$', 'display': True},
                    {'left': '\\(', 'right': '\\)', 'display': True},
                    {'left': '\\[', 'right': '\\]', 'display': True}
                ]
            )
            textbox = gr.MultimodalTextbox(
                interactive=True,
                file_count="multiple",
                placeholder=_("Ask me a question"),
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
    with gr.Blocks(css_paths=GRADIO_CSS, elem_classes=["footer"]) as blocks:
        with gr.Column():
            temp = gr.Slider(0.0, 2.0, value=0.6, step=0.1, label="temp", interactive=True)
            top_k = gr.Slider(20, 1000, value=50, step=1, label="top_k", interactive=True)
            rep_penalty = gr.Slider(0.0, 2.0, value=1.0, step=0.1, label="rep_penalty", interactive=True)
            new_tokens = gr.Slider(64, 8192, value=1024, step=1, label="new_tokens", interactive=True)
            sample = gr.Radio([True, False], value=False, label="sample", interactive=True)
            with gr.Column():
                with gr.Row(elem_classes=["update-button"]):
                    button_update = gr.Button(_("Update"), size="md", variant="primary")

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
    LOGGER.info("Loaded default settings")
    return {
        'temp': 0.6,
        'top_k': 50,
        'rep_penalty': 1.0,
        'new_tokens': 1024,
        'sample': False
    }

async def get_settings(request : gr.Request):
    url = f"http://{BASE_URL}/api/v1/user/settings"
    cookies = request.cookies.get('bonds')
    headers = {'Content-Type': 'application/json', 'Cookie': f"bonds={cookies}"}
    LOGGER.info("Fetching settings from: %s", url)
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, headers=headers)
    if response.status_code == 200:
        updated_settings = response.json()
        LOGGER.info("Settings received: %s", updated_settings)
        return (
            updated_settings["temp"],
            updated_settings["top_k"],
            updated_settings["rep_penalty"],
            updated_settings["new_tokens"],
            updated_settings["sample"],
        )  
    elif response.status_code == 401:
        LOGGER.warning("Unauthorized access to settings")
        raise gr.Error(_("Login to save settings"))
    else:
        LOGGER.error("Failed to fetch settings: %d", response.status_code)
        raise gr.Error(_("Failed to fetch settings: {code}").format(code=response.status_code))

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
    LOGGER.info("Updating settings at: %s with params: %s", url, params)
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.put(url, headers=headers, json=params)
    if response.status_code == 200:
        LOGGER.info("Settings successfully updated")
        return None
    if response.status_code == 401:
        LOGGER.warning("Unauthorized attempt to update settings")
        raise gr.Error(_(f"Login to save settings"))
    else:
        LOGGER.error("Failed to update settings: %d", response.status_code)
        raise gr.Error(_("Failed to update settings: {code}").format(code=response.status_code))


