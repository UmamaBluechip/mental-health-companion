import streamlit as st
import time
import pyaudio
import wave
import numpy as np
import soundfile as sf
from utils.functions import voice_to_text, get_gemini_response, text_to_audio
import pygame
import uuid


def main():
    st.set_page_config(page_title="Mental Health Chatbot", page_icon="💬", layout="wide")

    st.title("Mental Health Companion")

    st.markdown("<style>body {background-color: #282923; color: #c38d9e;}</style>", unsafe_allow_html=True)


    if "messages" not in st.session_state:
        st.session_state.messages = []

    chat_container = st.empty()

    if st.button("Speak"):
        with st.spinner(''):
            try:
                p = pyaudio.PyAudio()
                stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
                frames = []

                for i in range(0, int(5 * 44100 / 1024)):
                    data = stream.read(1024)
                    frames.append(data)

                stream.stop_stream()
                stream.close()
                p.terminate()

                wf = wave.open("user_audio.wav", 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(frames))
                wf.close()

                text_input = voice_to_text("user_audio.wav")
                print("Transcription:", text_input)

                if text_input != "Error during transcription":
                    st.session_state.messages.append({"role": "user", "content": text_input})
                    chat_container.markdown(f":speech_balloon: **You:** {text_input}")

                    response = get_gemini_response(text_input)
                    print("Gemini response:", response)

                    if response:
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        chat_container.markdown(f"**Chatbot:** {response}")

                        speech = text_to_audio(response)
                        print("Audio generated")
                        audio_filename = f"bot_response_{uuid.uuid4()}.wav"
                        speech = text_to_audio(response)
                        sf.write(audio_filename, speech["audio"], samplerate=speech["sampling_rate"])

                        with st.spinner('Chatbot responding...'):
                            pygame.mixer.init()
                            pygame.mixer.music.load(audio_filename)
                            pygame.mixer.music.play()
                            while pygame.mixer.music.get_busy():
                                time.sleep(1)

            except Exception as e:
                st.error(f"Error: {e}")

    for message in st.session_state.messages:
        with st.container():
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**Chatbot:** {message['content']}")

if __name__ == "__main__":
    main()
