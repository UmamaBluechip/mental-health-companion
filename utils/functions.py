import torch
from transformers import pipeline
import requests
import json
import soundfile as sf
import os
import google.generativeai as genai


def voice_to_text(audio_data, model_name="openai/whisper-small", device="cuda" if torch.cuda.is_available() else "cpu"):

  try:
    model = pipeline("automatic-speech-recognition", model=model_name, device=device, trust_remote_code=True)
    text = model(audio_data)["text"]
    return text
  
  except Exception as e:
    return f"Error during transcription"


def get_gemini_response(text):

  genai.configure(api_key=os.environ['API_KEY'])
  model = genai.GenerativeModel('gemini-1.5-flash')

  prompt = f"You are a compassionate and supportive mental health assistant. Provide helpful advice, encouragement, and information to the user. Respond in a warm and understanding tone. User: {text}"

  response = model.generate_content(prompt)
  return response.text



def text_to_audio(text):

  device = "cuda" if torch.cuda.is_available() else "cpu"
  model = pipeline("text-to-speech", model="parler-tts/parler_tts_mini_v0.1", device=device, trust_remote_code=True)

  audio_array = model(text)["audio"]
  return audio_array