import streamlit as st

from llm import LLM
from prompts import Prompts
from report_agent import ReportAgent
from database import Database
from streamlit_aux import Streamlit

st_aux = Streamlit()
db = Database()
rep = ReportAgent()
prompts = Prompts()
llm = LLM()

# ----------------- SESSION STATE -----------------
if "history" not in st.session_state:
    st.session_state["history"] = []
    initial_message = ("👋 Hello! I'm your AI Copilot. I can help you with:\n\n"
                       "1. 🔍 **Interpret** the chest X-ray\n"
                       "2. 📝 Generate a structured **report**\n"
                       "3. ⚡ Identify key **findings**\n\n"
                       "What would you like me to help you with?")
    st.session_state["history"].append({"user_message": initial_message, "assistant_message": None, "reasoning": None})

if "agent" not in st.session_state:
    st.session_state["agent"] = llm.agent()

if "current_case" not in st.session_state:
    st.session_state.current_case = None

if "report_generated" not in st.session_state:
    st.session_state.report_generated = False

if "processing" not in st.session_state:
    st.session_state.processing = False

# ----------------- HELPER FUNCTIONS -----------------
cases_df = db.generate_samples(3)

# --- HEADER ---
st.title("🏥 AI-Powered Radiology Workstation")

# --- MAIN LAYOUT ---
col1, col2, col3 = st.columns([1, 1, 1])

# --- WORKLIST & VIEWER ---
with col1:
    with st.container(border=True, height=600):
        st.subheader("📋 Patient Worklist")

        cols_cases = st.columns(len(cases_df))
        for idx, row in cases_df.iterrows():
            with cols_cases[idx]:
                if st.button(f'{row["Patient ID"]}', key=f'select_{idx}'):
                    st.session_state.current_case = idx + 1
                    st.session_state.history.append(
                        {"role": "assistant", "content": f"📋 Now viewing {row['Patient ID']}. How can I assist you?"})
                    st.rerun()

        st.divider()

        st.subheader("🖼️ Image Viewer")
        image_source = st.radio("Select image source:", ["Sample Image", "Upload Image", "Image URL"], horizontal=True)

        if image_source == "Sample Image":
            image_url = "https://upload.wikimedia.org/wikipedia/commons/a/a1/Normal_posteroanterior_%28PA%29_chest_radiograph_%28X-ray%29.jpg"
            img = st_aux.load_image_from_url(image_url)
        elif image_source == "Upload Image":
            uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])
            img = st_aux.load_image_from_upload(uploaded_file)
        else:
            url = st.text_input("Enter image URL:")
            img = st_aux.load_image_from_url(url) if url else None

        if img:
            st.image(img, use_container_width=True)
        else:
            st.info("Please select or upload an image")

# --- REPORT EDITOR ---
with col2:
    with st.container(border=True, height=600):
        st.subheader(f"📝 Report Editor")

        if "report_content" not in st.session_state:
            st.session_state.report_content = ""

        report_height = 480
        report_text = st.text_area("Report Content:", value=st.session_state.report_content, height=report_height,
                                   key="report_editor")
        st.session_state.report_content = report_text

# --- AI COPILOT ---
with col3:
    with st.container(border=True, height=600):
        st.subheader("🤖 AI Copilot")

        with st.container(height=450):
            for interaction in st.session_state["history"]:
                st.chat_message("user").write(interaction["user_message"])
                if interaction.get("assistant_message"):
                    st.chat_message("assistant").write(interaction["assistant_message"])

            # Show spinner while processing
            if st.session_state.processing:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = st.session_state["agent"].run(st.session_state["history"][-1]["user_message"])
                        assistant_message = llm.get_last_response(response)
                        reasoning = llm.get_reasoning_messages(response)

                        st.session_state["history"][-1]["assistant_message"] = assistant_message
                        st.session_state["history"][-1]["reasoning"] = reasoning
                        st.session_state.processing = False
                        st.rerun()

        if prompt := st.chat_input("💬 Ask me about the X-ray..."):
            st.session_state["history"].append({
                "user_message": prompt,
                "assistant_message": None,
                "reasoning": None
            })
            st.session_state.processing = True
            st.rerun()

st_aux.show_footer()