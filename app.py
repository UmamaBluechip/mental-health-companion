import torch
from transformers import pipeline

def voice_to_text(audio_data, model_name="openai/whisper-small", device="cuda" if torch.cuda.is_available() else "cpu"):

  try:
    model = pipeline("automatic-speech-recognition", model=model_name, device=device, trust_remote_code=True)
    text = model(audio_data)["text"]
    return text
  
  except Exception as e:
    return f"Error during transcription {e}"
  
