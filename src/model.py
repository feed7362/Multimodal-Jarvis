import os
import gradio as gr
import asyncio
from huggingface_hub import snapshot_download, login
from transformers import AutoTokenizer, AutoModelForCausalLM, SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan, pipeline
import numpy as np
import soundfile as sf
from datasets import load_dataset
import torch

from src.config import settings
from src.logger import CustomLogger
LOGGER = CustomLogger(__name__).logger

login(settings.HF_TOKEN)

def ensure_model_exists(model_path: str, repo_id: str):
    if not os.path.exists(model_path):
        LOGGER.warning(f"Model not found: {model_path}. Downloading from Hugging Face...")
        snapshot_download(repo_id=repo_id, local_dir=model_path)
    else:
        LOGGER.info(f"Model found: {model_path}.")

models = {
    # "nlp": (r"./models/nlp/Qwen2.5-1.5B-Instruct", "Qwen/Qwen2.5-1.5B-Instruct"),
    "stt": (r"./models/stt/whisper-large-v3-turbo", "openai/whisper-large-v3"),
    "tts": (r"./models/tts/Speecht5", "microsoft/speecht5_tts")
}

for key, (path, repo) in models.items():
    LOGGER.info(f"Ensuring model exists at {path} for {key}...")
    ensure_model_exists(path, repo)

# tokenizer = AutoTokenizer.from_pretrained(models["nlp"][0])
# LOGGER.info(f"Tokenizer loaded from {models['nlp'][0]}")
# 
# model = AutoModelForCausalLM.from_pretrained(
#     models["nlp"][0],
#     device_map="auto",
#     torch_dtype=torch.float16
# )
# LOGGER.info(f"Model loaded from {models['nlp'][0]}")

transcriber_model = pipeline("automatic-speech-recognition", model=models["stt"][0])
LOGGER.info(f"Transcriber model loaded from {models['stt'][0]}")

processor = SpeechT5Processor.from_pretrained(models["tts"][0])
model_speech = SpeechT5ForTextToSpeech.from_pretrained(models["tts"][0])
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)
LOGGER.info(f"Text-to-speech model loaded from {models['tts'][0]}")


# async def __bot_output__(history):
#     try:
#         history.append(gr.ChatMessage(role="assistant", content=""))
# 
#         text = tokenizer.apply_chat_template(
#             history,
#             tokenize=False,
#             add_generation_prompt=True,
#         )
# 
#         model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
#         generated_ids = model.generate(**model_inputs, max_new_tokens=512)
#         generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
#         generated_text  = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
#         
#         if not generated_text or not isinstance(generated_text, str):  
#             generated_text = "I'm sorry, but I couldn't generate a response."
# 
#         return history
# 
#     except Exception as e:
#         raise gr.Error(f"Failed to create text: {str(e)}")


async def __audiofile_to_text__(wav_path):
    try:
        audio_data, sample_rate = await asyncio.to_thread(sf.read, wav_path)

        audio_data = np.array(audio_data, dtype=np.float32)
        audio_data /= np.max(np.abs(audio_data))

        transcribed_text = await asyncio.to_thread(transcriber_model, {"raw": audio_data, "sampling_rate": sample_rate})

        return str(transcribed_text["text"])
    
    except Exception as e:
        raise gr.Error(f"Failed to transcribe audio: {e}")


async def __text_to_audiofile__(history):
    try:
        input_text = history[-1]["content"]
        inputs = processor(text=input_text, return_tensors="pt")
        speech = model_speech.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)
        speech = speech.numpy()
        sf.write(r"/src/data/audio/bark_out.wav", speech.numpy(), samplerate=16000)
        history.append(gr.ChatMessage(
            role="assistant",
            content=gr.Audio(r"/src/data/audio\bark_out.wav"),
            metadata={"title": rf"🛠️ Used tool {models['tts'][0]}"}
        ))
        return history
    except Exception as e:
        raise gr.Error(f"Failed to convert text to audio: {e}")
