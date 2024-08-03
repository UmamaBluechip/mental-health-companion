import streamlit as st
import pyaudio
import wave
import tempfile
import os
import uuid
from utils.functions import voice_to_text, get_gemini_response, text_to_audio

# Directories for audio files
USER_AUDIO_DIR = 'user_audio'
BOT_AUDIO_DIR = 'bot_audio'

# Create directories if they do not exist
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

    # Save the recorded data as a WAV file
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
    st.title("Mental Health Voice Chat")

    # Initialize chat history
    if 'history' not in st.session_state:
        st.session_state.history = []

    # Include custom CSS for chat bubble styling
    st.markdown("""
    <style>
    .user-message {
        background-color: #dcf8c6;
    }
    .bot-message {
        background-color: #f1f0f0;

    }
    .chat-container {
        display: flex;
    }

    </style>
    """, unsafe_allow_html=True)

    # UI Elements
    st.write("Click 'Record' to start recording your message.")
    record_button = st.button("Record")
    
    if record_button:
        # Record the audio
        audio_file = record_audio(duration=5)  # Record for 5 seconds
        if audio_file:
            st.session_state.history.append({'type': 'user', 'file': audio_file})

            # Display user message
            st.markdown(f'<div class="user-message"><audio class="audio-player" controls src="{audio_file}"></audio></div>', unsafe_allow_html=True)
            
            # Convert voice message to text and get chatbot response
            user_text = voice_to_text(audio_file)
            if user_text:
                response_text = get_gemini_response(user_text)
                if response_text:
                    response_audio = text_to_audio(response_text)

                    # Save response audio to a file
                    response_file = os.path.join(BOT_AUDIO_DIR, f"{uuid.uuid4()}.wav")
                    try:
                        with open(response_file, 'wb') as f:
                            f.write(response_audio)
                        st.session_state.history.append({'type': 'bot', 'file': response_file})

                        # Display bot response
                        st.markdown(f'<div class="bot-message"><audio class="audio-player" controls src="{response_file}"></audio></div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error saving bot response audio file: {e}")
                else:
                    st.error("Failed to get a response from the chatbot.")
            else:
                st.error("Failed to transcribe voice message.")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.history:
            if message['type'] == 'user':
                st.markdown(f'<div class="user-message"><audio class="audio-player" controls src="{message["file"]}"></audio></div>', unsafe_allow_html=True)
            elif message['type'] == 'bot':
                st.markdown(f'<div class="bot-message"><audio class="audio-player" controls src="{message["file"]}"></audio></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
