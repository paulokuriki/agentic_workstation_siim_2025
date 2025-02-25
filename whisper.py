import time
import os
import streamlit as st
from openai import OpenAI
import tempfile
import wave
import constants as c

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
        if "audio_key" not in st.session_state:
            st.session_state.audio_key = 0

    def get_audio_duration(self, file_path):
        with wave.open(file_path, "rb") as audio:
            frames = audio.getnframes()
            rate = audio.getframerate()
            duration = frames / float(rate)
        return duration

    def crop_audio(self, input_file_path, max_duration=c.MAX_DURATION_AUDIO):
        # Create a new temporary file for cropped output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_cropped:
            cropped_path = temp_cropped.name

        # Read and crop from input file
        with wave.open(input_file_path, "rb") as audio:
            params = audio.getparams()
            rate = audio.getframerate()
            frames = audio.getnframes()
            duration = frames / float(rate)

            # If duration is fine, just copy the file
            if duration <= max_duration:
                with wave.open(cropped_path, "wb") as dst_audio:
                    dst_audio.setparams(params)
                    dst_audio.writeframes(audio.readframes(frames))
            else:
                # Crop to max duration
                max_frames = int(rate * max_duration)
                with wave.open(cropped_path, "wb") as dst_audio:
                    st.toast(f"Your message was cropped to {max_duration} seconds.", icon="🚨")
                    time.sleep(3)
                    dst_audio.setparams(params)
                    dst_audio.writeframes(audio.readframes(max_frames))

        return cropped_path

    def show_audio_input(self):
        audio_file = st.audio_input("Talk to the Co-Pilot:",
                                    key=f"audio_input_{st.session_state.audio_key}",
                                    label_visibility="collapsed")

        def run_button_command(command_message):
            st.session_state["history"].append(
                {"user_message": command_message, "assistant_message": None, "reasoning": None}
            )
            st.session_state.processing = True

            # Increment the audio key to force a new widget instance
            st.session_state.audio_key += 1

            st.rerun()

        if audio_file:
            input_file_path = None
            cropped_file_path = None

            try:
                # Save input audio to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                    temp_file.write(audio_file.read())
                    input_file_path = temp_file.name

                # Process the audio and get path to cropped file
                cropped_file_path = self.crop_audio(input_file_path)

                # Get duration for logging
                with wave.open(cropped_file_path, "rb") as audio:
                    frames = audio.getnframes()
                    rate = audio.getframerate()
                    duration = frames / float(rate)
                    print(f"Processed Audio Duration: {duration:.2f} seconds")

                # Transcribe
                with open(cropped_file_path, "rb") as audio:
                    transcription = self.transcriber.transcribe_audio(audio)
                    if transcription:
                        run_button_command(transcription)
                        print(transcription)
                    else:
                        st.error("Failed to transcribe audio. Please try again.")

            except Exception as e:
                st.error(f"Error processing audio: {str(e)}")
            finally:
                # Clean up both temporary files
                for file_path in [input_file_path, cropped_file_path]:
                    if file_path and os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except PermissionError:
                            pass  # Let OS clean up if file is still locked


if __name__ == "__main__":
    whisper = StreamlitWhisperApp()
    whisper.show_audio_input()
