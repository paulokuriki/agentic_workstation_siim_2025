from PIL import Image
from io import BytesIO
import requests
import streamlit as st
from llm import LLM

llm = LLM()


class Streamlit:
    def __init__(self):
        # ----------------- STREAMLIT UI -----------------
        st.set_page_config(
            layout="wide",
            page_title="AI-Powered Radiology Workstation",
            initial_sidebar_state="collapsed"
        )

        # Custom CSS for better styling

    # ----------------- IMAGE HANDLING -----------------
    def load_image_from_url(self, url):
        if url:
            try:
                response = requests.get(url)
                return Image.open(BytesIO(response.content))
            except:
                return None
        else:
            return None

    def load_image_from_upload(self, uploaded_file):
        if uploaded_file is not None:
            try:
                return Image.open(uploaded_file)
            except:
                return None
        return None

    # --- FOOTER ---
    @staticmethod
    def show_footer():
        buttons = {
            "🔍 **`analyse`**": "Analyze image",
            "📝 **`generate report`**": "Generate report",
            "📝 **`make changes in report`**": "Make changes in report",
            "⚡ **`identify findings in report`**": "Identify findings in report",
            "✅ **`sign report`**": "Sign report",
        }

        def run_button_command(command_message):
            st.session_state["history"].append(
                {"user_message": command_message, "assistant_message": None, "reasoning": None}
            )
            st.session_state.processing = True
            st.rerun()

        with st.container(border=True):
            st.write("""### Available Commands:""")
            columns = st.columns(len(buttons))

            for col, (button_text, command_message) in zip(columns, buttons.items()):
                with col:
                    if st.button(button_text):
                        run_button_command(command_message)

