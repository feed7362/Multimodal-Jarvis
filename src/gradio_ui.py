from src.model import __audiofile_to_text__
import httpx 
import gradio as gr

__GRADIO_CSS__ = 'src/static/custom_gradio.css'
BASE_URL = 'http://127.0.0.1:8000'
AGENT_ID = 'chat'
HEADERS = {'Content-Type': 'application/json'}

async def create_session():
    url = f"{BASE_URL}/api/v1/agents/{AGENT_ID}/sessions"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("id")
        return None
    except httpx.RequestError as exc:
        return None

async def send_message(session_id, message):
    url = f"{BASE_URL}/api/v1/sessions/{session_id}/messages"
    payload = {"role": "user", "content": message}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, headers=HEADERS, json=payload)
        return response.json()
    except httpx.RequestError as exc:
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

async def __add_message__(message, history, state): # {'text': '123', 'files': []}
    try:
        if "session_id" not in state:
            session_id = await create_session()  # Create a new session if it doesn't exist
            state["session_id"] = session_id
        
        if message is not None:
            session_id = state.get("session_id")
            history.append({"role": "user", "content": message["text"]}) 
            
        if message and len(message["files"]) > 0:
            for file_path in message["files"]:
                    if file_path.endswith(".wav"):
                        transcribed_text = await __audiofile_to_text__(file_path)
                        history.append({"role": "user", "content":  file_path, "metadata": {"title": "🎤 User audio"}})
                        history.append({"role": "user", "content": transcribed_text})
                    
        response_data = await send_message(session_id, history[-1]["content"]) 
        bot_reply = response_data.get("response", "No response")
        history.append({"role": "assistant", "content": bot_reply})

        state["history"] = history
        print(state)
        if response_data.get("state") == "WAITING_FOR_CONFIRMATION":
            yield bot_reply, state
            
        yield bot_reply, state

    except Exception as e:
        raise gr.Error("Unsupported type of file message received")


def create_chat_ui():
    with gr.Blocks(css_paths=__GRADIO_CSS__) as blocks:
      with gr.Column(elem_classes=["footer"], show_progress=True):
        state = gr.State({})
        chat = gr.Chatbot( 
            height=600,
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
    with gr.Blocks(css_paths=__GRADIO_CSS__) as blocks:
       with gr.Column(elem_classes=["footer"], show_progress=True):
        res_temp = gr.Slider(0.0, 2.0, 1.0, step=0.1, label="temp", interactive=True)
        res_topk = gr.Slider(20, 1000, 50, step=1, label="top_k", interactive=True)
        res_rpen = gr.Slider(0.0, 2.0, 1.2, step=0.1, label="rep_penalty", interactive=True)
        res_mnts = gr.Slider(64, 8192, 512, step=1, label="new_tokens", interactive=True)
        res_sample = gr.Radio([True, False], value=True, label="sample", interactive=True)

    return blocks

