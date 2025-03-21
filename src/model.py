import gradio as gr
import asyncio
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import pipeline
import numpy as np
import torch
from scipy.io import wavfile

model_name_nlp = r"Q:\Projects\Multimodal-Jarvis\models\nlp\Qwen2.5-1.5B-Instruct"
model_name_stt = r"Q:\Projects\Multimodal-Jarvis\models\stt\whisper-large-v3-turbo"
model_name_tts = r"Q:\Projects\Multimodal-Jarvis\models\tts\Suno-Bark"

tokenizer = AutoTokenizer.from_pretrained(model_name_nlp)
model = AutoModelForCausalLM.from_pretrained(
    model_name_nlp, 
    device_map="auto", 
    torch_dtype="auto"
)
transcriber_model = pipeline("automatic-speech-recognition", model = model_name_stt)
synthesiser = pipeline("text-to-speech", model = model_name_tts)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using {device} for inference")


async def __bot_output__(history):
    try:
        history.append(gr.ChatMessage(role="assistant", content=""))

        text = tokenizer.apply_chat_template(
            history,
            tokenize=False,
            add_generation_prompt=True,
        )

        model_inputs  = tokenizer([text], return_tensors="pt").to(model.device)
        generated_ids = model.generate(**model_inputs, max_new_tokens=512)
        generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
        generated_text  = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        if not generated_text or not isinstance(generated_text, str):  
            generated_text = "I'm sorry, but I couldn't generate a response."

        return history

    except Exception as e:
        raise gr.Error(f"Failed to create text: {str(e)}")


async def __audiofile_to_text__(wav_path):
    try:
        sample_rate, audio_data = await asyncio.to_thread(wavfile.read, wav_path)

        audio_data = np.array(audio_data, dtype=np.float32)
        audio_data /= np.max(np.abs(audio_data))

        transcribed_text = await asyncio.to_thread(transcriber_model, {"raw": audio_data, "sampling_rate": sample_rate})

        return str(transcribed_text["text"])
    
    except Exception as e:
        raise gr.Error(f"Failed to transcribe audio: {e}")


async def __text_to_audiofile__(history):
    try:
        input_text = history[-1]["content"]
        speech = synthesiser(input_text, forward_params = {"do_sample": True})
        rate_speech = speech["sampling_rate"]
        data_speech = speech["audio"]
        data_speech = data_speech.flatten()
        data_speech = np.int16(data_speech / np.max(np.abs(data_speech)) * 32767)

        wavfile.write(r"Q:\Projects\Multimodal-Jarvis\data\audio\bark_out.wav", rate=rate_speech, data=data_speech)
        history.append(gr.ChatMessage(
            role = "assistant", 
            content = gr.Audio(r"Q:\Projects\Multimodal-Jarvis\data\audio\bark_out.wav"),
            metadata = {"title": rf"🛠️ Used tool {model_name_tts}"}
        ))
        return history
    except Exception as e:
        raise gr.Error(f"Failed to convert text to audio: {e}")
