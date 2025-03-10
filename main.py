import time
import pandas as pd

import streamlit as st
from streamlit_aux import Streamlit
from whisper import StreamlitWhisperApp

# start up streamlit config first
st_aux = Streamlit()
whisper = StreamlitWhisperApp()

from llm import LLM
from prompts import Prompts
from report_agent import ReportAgent
from database import Database
from emr_loader import search_records
from call_functions import load_case

import constants as c

db = Database()
rep = ReportAgent()
prompts = Prompts()
llm = LLM()

container_height = 780

# ----------------- SESSION STATE -----------------
if "history" not in st.session_state:
    st.session_state["history"] = []
    initial_message = ("👋 Hello! I'm your AI Copilot. I can help you with:\n\n"
                       "1. 🔍 **Analyze** the chest X-ray\n"
                       "2. 📝 Generate a structured **report**\n"
                       "3. ⚡ Identify key **findings**\n\n"
                       "What would you like me to help you with?")
    st.session_state["history"].append({"user_message": initial_message, "assistant_message": None, "reasoning": None})

if "agent" not in st.session_state:
    st.session_state["agent"] = llm.agent()

if "report_text" not in st.session_state:
    st.session_state.report_text = ""

if "processing" not in st.session_state:
    st.session_state.processing = False

if "cases_df" not in st.session_state:
    st.session_state.cases_df = db.generate_samples()

if "image_url" not in st.session_state:
    st.session_state.image_url = None

if "notification_email" not in st.session_state:
    st.session_state.notification_email = None  # default email

if "df_chart" not in st.session_state:
    st.session_state.df_chart = None

tab_workstation, tab_emr = st.tabs(["🏥 **AI Workstation**", "📂 **Access Electronic Medical Records**"])

with tab_workstation:
    # --- HEADER ---
    st.title("🏥 AI-Powered Radiology Workstation")

    # --- MAIN LAYOUT ---
    col1, col2, col3 = st.columns([0.8, 0.8, 1])

    # --- WORKLIST & VIEWER ---
    with col1:
        with st.container(border=True, height=container_height):
            st.subheader("📋 Patient Worklist")
            cols_cases = st.columns(len(st.session_state.cases_df))
            sample_case_url = "https://upload.wikimedia.org/wikipedia/commons/a/a1/Normal_posteroanterior_%28PA%29_chest_radiograph_%28X-ray%29.jpg"
            for idx, row in st.session_state.cases_df.iterrows():
                with cols_cases[idx]:
                    if st.button(f'**Study ID**:  {row["id"]}', key=f'select_{row["id"]}'):
                        load_case(row["id"])
                        #st.session_state.image_url = row["url"]
                        #st.session_state.study_id = row["id"]
                        #st.session_state["history"].append(
                        #    {"user_message": None,
                        #     "assistant_message": f"📋 Now viewing case {row['id']}. How can I assist you?",
                        #     "reasoning": None})
                        #st.session_state.report_text = ""
                        st.rerun()

            st.divider()

            st.subheader("🖼️ Image Viewer")
            image_source = st.radio("Select image source:", ["Sample Image", "Image URL"], horizontal=True)

            if image_source == "Sample Image":
                img = st_aux.load_image_from_url(st.session_state.image_url)
            else:
                url = st.text_input("Enter image URL:")
                img = st_aux.load_image_from_url(url)  # if url else None
                st.session_state.image_url = url
                st.session_state.study_id = ""
                st.session_state.report_text = ""

            if img:
                st.image(img, use_container_width=True, )
            else:
                st.warning(
                    "🔍 No image selected yet! Choose a case from the worklist or enter an image URL to begin viewing.")

    # --- REPORT EDITOR ---
    with col2:
        with st.container(border=True, height=container_height):
            st.subheader(f"📝 Report Editor")

            if "report_text" not in st.session_state:
                st.session_state.report_text = ""

            container_internal_height = 95
            report_height = container_height - container_internal_height
            report_text = st.text_area("Report", value=st.session_state.report_text, height=report_height,
                                       key="report_editor", label_visibility="collapsed")
            st.session_state.report_text = report_text

    # --- AI COPILOT ---
    with col3:
        with st.container(border=True, height=container_height):
            st.subheader("🤖 AI Copilot")

            container_internal_height = 235
            with st.container(height=container_height - container_internal_height):
                for interaction in st.session_state["history"]:
                    if interaction.get("user_message"):
                        st.chat_message("user").write(interaction["user_message"])

                    if interaction.get("assistant_message"):
                        with st.chat_message("assistant"):
                            st.write(interaction["assistant_message"])

                            if interaction.get("reasoning"):
                                with st.expander("**Understand agent reasoning...**"):
                                    with st.container(border=True):
                                        st.code(interaction["reasoning"])

                # Show spinner while processing
                if st.session_state.processing:
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            max_try = 3
                            current_try = 0
                            while current_try < max_try:
                                try:
                                    response = st.session_state["agent"].run(
                                        st.session_state["history"][-1]["user_message"])
                                    assistant_message = llm.get_last_response(response)
                                    reasoning = llm.get_reasoning_messages(response)

                                    st.session_state["history"][-1]["assistant_message"] = assistant_message
                                    st.session_state["history"][-1]["reasoning"] = reasoning
                                    st.session_state.processing = False
                                    break
                                except Exception as e:
                                    time.sleep(2)
                                    current_try = current_try + 1
                                    assistant_message = e
                                    reasoning = None
                                    if current_try == max_try:
                                        st.session_state["history"][-1]["assistant_message"] = assistant_message
                                        st.session_state["history"][-1]["reasoning"] = reasoning
                                        st.session_state.processing = False
                                    continue

                            st.rerun()

            if not st.session_state.processing:
                if prompt := st.chat_input("💬 Ask me about the X-ray..."):
                    st.session_state["history"].append({
                        "user_message": prompt,
                        "assistant_message": None,
                        "reasoning": None
                    })
                    st.session_state.processing = True
                    st.rerun()

                whisper.show_audio_input()

    st_aux.show_footer()

with tab_emr:
    st.title("📂 Electronic Medical Records")

    # --- MAIN LAYOUT ---
    col1, col2, col3 = st.columns([0.7, 1, 1])

    # --- SEARCH SECTION ---
    with col1:
        with st.container(border=True, height=container_height):
            st.subheader("🔍 Search Tools")
            st.write(
                "Use the options below to look up patient in the HIS or study records in the PACS. "
                "Then click **Search** to see matching results."
            )
            search_type = st.radio("Search by:", ["Study ID", "Patient MRN"], horizontal=True)
            search_field = st.text_input(f"Searching by {search_type}:",
                                         placeholder=f"Enter {search_type} here...")

            if st.button("Search", use_container_width=True):
                st.session_state.df_chart = search_records(search_type=search_type, search_field=search_field)
                try:
                    del st.session_state.selected_record
                except:
                    pass
                st.rerun()

    # --- SEARCH RESULTS ---
    with col2:
        with st.container(border=True, height=container_height):
            if search_type == "Patient MRN":
                st.subheader("📋 Search Results from HIS")
            else:
                st.subheader("📋 Search Results from PACS")


            if st.session_state.df_chart is not None :
                if len(st.session_state.df_chart) > 0:
                    selection = st.dataframe(st.session_state.df_chart, use_container_width=True,
                                             selection_mode=["single-row"], on_select="rerun", hide_index=True)
                    st.caption("Select a row (checkbox on the left) to load details.")
                    selected_rows = selection.selection.get("rows", [])

                    if len(selected_rows) > 0:
                        idx = selected_rows[0]
                        selected_indices = st.session_state.df_chart.iloc[[idx]]
                        st.session_state.selected_record = selected_indices
                    else:
                        try:
                            del st.session_state.selected_record
                        except:
                            pass
                else:
                    st.info("No results found.")
            else:
                st.info("No search performed yet or no results found.")

    # --- DETAILS VIEW ---
    with col3:
        with st.container(border=True, height=container_height):
            st.subheader("🗃️ Record Details")

            if "selected_record" in st.session_state:
                # Extract the single row (Series) from the stored DataFrame
                record = st.session_state.selected_record.iloc[0]

                # Build a Markdown string from all columns
                details_md = []
                for col_name in record.index:
                    val = record.get(col_name, "N/A")
                    if pd.notna(val) and val != "N/A":
                        details_md.append(f"**{str(col_name).replace('_', ' ')}**: {val}")

                container_internal_height = 95
                with st.container(border=True, height=container_height - container_internal_height):
                    if search_type == "Patient MRN":
                        with st.spinner("Retrieving patient chart (EMR) from HIS..."):
                            time.sleep(4)
                    else:
                        with st.spinner("Retrieving study order from PACS..."):
                            time.sleep(1.5)

                    # Join each line with a double newline for spacing
                    st.markdown("\n\n".join(details_md))

            else:
                st.info("Select a record in the 'Search Results' column to view its details.")
