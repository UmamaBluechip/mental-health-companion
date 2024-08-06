import streamlit as st
import pyaudio
import wave
import os
import uuid
from utils.functions import voice_to_text, get_gemini_response, text_to_audio


USER_AUDIO_DIR = 'user_audio'
BOT_AUDIO_DIR = 'bot_audio'

os.makedirs(USER_AUDIO_DIR, exist_ok=True)
os.makedirs(BOT_AUDIO_DIR, exist_ok=True)

def record_audio(duration=5):
    """Record audio from the microphone for a given duration."""
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = duration
    WAVE_OUTPUT_FILENAME = os.path.join(USER_AUDIO_DIR, f"{uuid.uuid4()}.wav")

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []

    try:
        st.write("Recording...")
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        st.write("Message sent.")
    except Exception as e:
        st.error(f"Error recording audio: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

    try:
        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
    except Exception as e:
        st.error(f"Error saving audio file: {e}")
        return None

    return WAVE_OUTPUT_FILENAME

def main():

    if 'history' not in st.session_state:
        st.session_state.history = []

    st.markdown("""
    <style>
    body {
        background-color: #ffffff;
        color: #333;
        font-family: 'Arial', sans-serif;
    }
    .user-message {
        background-color: #e6f9f4;
        color: #333;
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 10px;
        max-width: 80%;
        align-self: flex-start;
    }
    .bot-message {
        background-color: #ffffff;
        color: #333;
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 10px;
        max-width: 80%;
        align-self: flex-end;
        border: 1px solid #e0e0e0;
    }
    
    audio::-webkit-media-controls-panel,
    audio::-webkit-media-controls-enclosure {
        background-color: #2dbd6e;
        max-width: 70%;
        max-height: 50px;
    }

    .chat-container {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }
    .record-button {
        background-color: #2dbd6e;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        cursor: pointer;
        font-size: 16px;
        margin-bottom: 20px;
    }
    .record-button:hover {
        background-color: #28a864;
    }
    .title {
        color: #2dbd6e;
        margin-bottom: 20px;
    }

    .chats {
        color: gray;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='title'>Mental Health Voice Chat</h1>", unsafe_allow_html=True)
    st.write("Click 'Record' to start recording your message.")
    record_button = st.button("Record", key="record", help="Start recording your message")

    if record_button:
        audio_file = record_audio(duration=5)
        if audio_file:
            st.session_state.history.append({'type': 'user', 'file': audio_file})

            st.markdown('**👤 You:**', unsafe_allow_html=True)
            st.audio(audio_file, format='audio/wav')

            user_text = voice_to_text(audio_file)
            print(user_text)
            if user_text:
                response_text = get_gemini_response(user_text)
                if response_text:
                    response_file = os.path.join(BOT_AUDIO_DIR, f"{uuid.uuid4()}.wav")
                    audio_result = text_to_audio(response_text, response_file)

                    if os.path.exists(response_file) and os.path.getsize(response_file) > 0:
                        st.session_state.history.append({'type': 'bot', 'file': response_file})

                        st.markdown('**🤖 Bot:**', unsafe_allow_html=True)
                        st.audio(response_file, format='audio/wav')
                    else:
                        st.error(f"Failed to create bot response audio: {audio_result}")
                else:
                    st.error("Failed to get a response from the chatbot.")
            else:
                st.error("Failed to transcribe voice message.")
    
    chat_container = st.container()
    with chat_container:
        st.markdown("<h3 class='history'>Chats</h3>", unsafe_allow_html=True)
        for message in st.session_state.history:
            if message['type'] == 'user':
                st.markdown('**👤 You:**', unsafe_allow_html=True)
                st.audio(message["file"], format='audio/wav')
            elif message['type'] == 'bot':
                st.markdown('**🤖 Bot:**', unsafe_allow_html=True)
                st.audio(message["file"], format='audio/wav')

if __name__ == "__main__":
    main()
