import os
import streamlit as st
from openai import OpenAI
import tempfile
import wave


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

    def get_audio_duration(self, file_path):
        with wave.open(file_path, "rb") as audio:
            frames = audio.getnframes()
            rate = audio.getframerate()
            duration = frames / float(rate)
        return duration

    def crop_audio(self, file_path, max_duration=10):
        with wave.open(file_path, "rb") as audio:
            params = audio.getparams()
            frames = audio.getnframes()
            rate = audio.getframerate()
            duration = frames / float(rate)

            if duration > max_duration:
                max_frames = int(rate * max_duration)
                with wave.open(file_path, "rb") as src_audio, wave.open(file_path, "wb") as dst_audio:
                    dst_audio.setparams(params)
                    dst_audio.writeframes(src_audio.readframes(max_frames))
        return file_path

    def show_audio_input(self):
        audio_file = st.audio_input("Talk to the Co-Pilot:", label_visibility="collapsed")

        def run_button_command(command_message):
            st.session_state["history"].append(
                {"user_message": command_message, "assistant_message": None, "reasoning": None}
            )
            st.session_state.processing = True
            st.rerun()

        if audio_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_file.read())
                temp_file_path = temp_file.name

            self.crop_audio(temp_file_path)

            audio_duration = self.get_audio_duration(temp_file_path)
            print(f"Processed Audio Duration: {audio_duration:.2f} seconds")

            with open(temp_file_path, "rb") as audio:
                transcription = self.transcriber.transcribe_audio(audio)
                run_button_command(transcription)
                print(transcription)

            os.remove(temp_file_path)


if __name__ == "__main__":
    whisper = StreamlitWhisperApp()
    whisper.show_audio_input()
