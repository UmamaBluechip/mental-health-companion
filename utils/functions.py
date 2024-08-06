import torch
from transformers import pipeline, AutoTokenizer
from parler_tts import ParlerTTSForConditionalGeneration
from datasets import load_dataset
import requests
import json
import io
import soundfile as sf
import os
import google.generativeai as genai


def voice_to_text(audio_data):

  try:
     
     auth_key = os.environ['AUTH_KEY']
     
     API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
     headers = {"Authorization": f"Bearer {auth_key}"}
     
     def query(audio_data):
        with open(audio_data, "rb") as f:
           data = f.read()
           response = requests.post(API_URL, headers=headers, data=data)
           return response.json()
        
     response = query(audio_data)

     text = response['text']

     return text
        
  except Exception as e:
    return f"Error during transcription"


def get_gemini_response(text):

  genai.configure(api_key=os.environ['API_KEY'])
  model = genai.GenerativeModel('gemini-1.5-flash')

  prompt = f"You are a compassionate and supportive mental health assistant. Provide helpful advice, encouragement, and information to the user. Respond in a warm and understanding tone. mostly try to keep the response short. User: {text}"

  response = model.generate_content(prompt)
  return response.text



def text_to_audio(text, output_file):
    try:
        synthesiser = pipeline("text-to-speech", "microsoft/speecht5_tts")

        embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
        speaker_embedding = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)

        speech = synthesiser(text, forward_params={"speaker_embeddings": speaker_embedding})

        sf.write(output_file, speech["audio"], samplerate=speech["sampling_rate"])

        return output_file

    except Exception as e:
        return f"Error during text to audio conversion: {e}"