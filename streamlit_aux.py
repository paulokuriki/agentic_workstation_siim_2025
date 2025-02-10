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
        st.markdown("""
            <style>
            .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
                font-size: 1.2rem;
            }
            .reportSection {
                background-color: #f0f2f6;
                padding: 10px;
                border-radius: 5px;
                margin: 5px 0;
            }
            </style>
        """, unsafe_allow_html=True)

    # ----------------- IMAGE HANDLING -----------------
    def load_image_from_url(self, url):
        try:
            response = requests.get(url)
            return Image.open(BytesIO(response.content))
        except:
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
        with st.container(border=True):
            st.markdown("""
            **Available Commands:**
            • 🔍 `interpret` - Detailed image analysis
            • 📝 `generate report` - Create structured report
            • ⚡ `findings` - Identify key observations
            • ✅ `sign report` - Finalize report
            """)
