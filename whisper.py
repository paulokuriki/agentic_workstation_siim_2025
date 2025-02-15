import os
import streamlit as st
from openai import OpenAI
import tempfile


class WhisperTranscriber:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def transcribe_audio(self, audio_file):
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
        return transcription


class StreamlitWhisperApp:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.transcriber = WhisperTranscriber(api_key)

    def show_audio_input(self):
        audio_file = st.audio_input("Talk to the Co-Pilot:", label_visibility="hidden")

        def run_button_command(command_message):
            st.session_state["history"].append(
                {"user_message": command_message, "assistant_message": None, "reasoning": None}
            )
            st.session_state.processing = True
            st.rerun()

        if audio_file:
            with st.spinner("Thinking..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                    temp_file.write(audio_file.read())
                    temp_file_path = temp_file.name

                with open(temp_file_path, "rb") as audio:
                    transcription = self.transcriber.transcribe_audio(audio)
                    run_button_command(transcription)
                    print(transcription)


if __name__ == "__main__":
    whisper = StreamlitWhisperApp()
    whisper.show_audio_input()
