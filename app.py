import streamlit as st
import time
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import soundfile as sf
from utils.functions import voice_to_text, get_gemini_response, text_to_audio
import pygame

def main():
    st.title("Mental Health Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.container():
            if message["role"] == "user":
                st.markdown(f":speech_balloon: **You:** {message['content']}")
            else:
                st.markdown(f":robot: **Chatbot:** {message['content']}")

    if st.button("Speak"):
        with st.spinner('Recording...'):
            try:
                fs = 44100
                seconds = 5
                myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
                sd.wait()
                audio_file = "user_audio.wav"
                write(audio_file, fs, myrecording)

                text_input = voice_to_text(audio_file)
                if text_input != "Error during transcription":
                    st.session_state.messages.append({"role": "user", "content": text_input})
                    response = get_gemini_response(text_input)
                    if response:
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        audio_array = text_to_audio(response)
                        bot_audio_file = "bot_audio.wav"
                        sf.write(bot_audio_file, audio_array, 44100)
                        pygame.mixer.init()
                        pygame.mixer.music.load(bot_audio_file)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            time.sleep(1)
            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
