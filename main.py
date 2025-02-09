import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import datetime
import pandas as pd

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

# ----------------- SESSION STATE -----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hello! I'm your AI Copilot. I can help you with:\n\n" +
                                         "1. 🔍 **Interpret** the chest X-ray\n" +
                                         "2. 📝 Generate a structured **report**\n" +
                                         "3. ⚡ Identify key **findings**\n\n" +
                                         "What would you like me to help you with?"}
    ]

if "current_case" not in st.session_state:
    st.session_state.current_case = None

if "report_generated" not in st.session_state:
    st.session_state.report_generated = False

if "report_status" not in st.session_state:
    st.session_state.report_status = "Draft"


# ----------------- HELPER FUNCTIONS -----------------
def generate_structured_report(patient_id):
    """Generate a structured radiology report"""
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    report = f"""STATUS: {st.session_state.report_status}
EXAM DATE: {current_date}
PATIENT ID: {patient_id}

FINDINGS:
• Lung fields are clear and well-expanded
• No focal consolidation, effusion, or pneumothorax
• No suspicious pulmonary nodules or masses
• Heart size is within normal limits
• Mediastinal contours appear normal
• Aortic arch is unremarkable
• Bony thoracic cage shows no acute abnormality
• Soft tissues are unremarkable
• No suspicious calcifications

IMPRESSION:
1. Normal chest radiograph
2. No acute cardiopulmonary process

[AI Generated Report - Requires Radiologist Review]"""
    return report


# ----------------- DUMMY DATABASE -----------------
# Simplified cases data for table display
num_samples = 3
cases_data = {
    'Patient ID': [f'**Patient ID:** {1000 + i}' for i in range(1, num_samples + 1)],
    'Action': ['Select' for _ in range(num_samples)]
}
cases_df = pd.DataFrame(cases_data)


# ----------------- IMAGE HANDLING -----------------
def load_image_from_url(url):
    try:
        response = requests.get(url)
        return Image.open(BytesIO(response.content))
    except:
        return None


def load_image_from_upload(uploaded_file):
    if uploaded_file is not None:
        try:
            return Image.open(uploaded_file)
        except:
            return None
    return None


def process_user_message(message):
    """Process user messages and generate appropriate responses"""
    message_lower = message.lower()

    if "interpret" in message_lower or "analysis" in message_lower:
        return "🔍 I'll analyze the image systematically. Which area should I focus on first?\n\n" + \
            "• Lung fields and pleural spaces\n" + \
            "• Cardiac silhouette and vessels\n" + \
            "• Bones and soft tissues\n" + \
            "• Overall impression"

    elif "report" in message_lower or "generate" in message_lower:
        current_patient = f"Patient {1000 + st.session_state.current_case}"
        report = generate_structured_report(current_patient)
        st.session_state.current_report = report
        st.session_state.report_generated = True
        return "📝 I've generated a structured report in the editor. Would you like me to:\n\n" + \
            "• Explain any specific findings\n" + \
            "• Modify any sections\n" + \
            "• Add additional observations"

    elif "sign" in message_lower:
        st.session_state.report_status = "Final"
        return "✅ Report status changed to FINAL. Would you like me to generate a signature block?"

    elif "finding" in message_lower:
        return "⚡ I'll analyze key findings. Select an area to focus on:\n\n" + \
            "• Pulmonary findings\n" + \
            "• Cardiovascular status\n" + \
            "• Skeletal structures\n" + \
            "• Soft tissue abnormalities"

    else:
        return "I can help with:\n\n" + \
            "• Interpreting the X-ray\n" + \
            "• Generating reports\n" + \
            "• Identifying findings\n" + \
            "• Signing reports\n\n" + \
            "What would you like me to focus on?"


# --- HEADER ---
st.title("🏥 AI-Powered Radiology Workstation")

# --- MAIN LAYOUT ---
col1, col2, col3 = st.columns([1, 1, 1])

# --- WORKLIST & VIEWER ---
with col1:
    with st.container(border=True, height=600):
        st.subheader("📋 Patient Worklist")

        # Display cases as a table
        for idx, row in cases_df.iterrows():
            cols = st.columns([3, 1])
            with cols[0]:
                st.write(row['Patient ID'])
            with cols[1]:
                if st.button('Select', key=f'select_{idx}'):
                    st.session_state.current_case = idx + 1
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"📋 Now viewing {row['Patient ID']}. How can I assist you?"
                    })
                    st.rerun()

        st.divider()

        # Image Upload Section
        st.subheader("🖼️ Image Viewer")

        # Image source selection
        image_source = st.radio("Select image source:",
                                ["Sample Image", "Upload Image", "Image URL"],
                                horizontal=True)

        if image_source == "Sample Image":
            image_url = "https://upload.wikimedia.org/wikipedia/commons/a/a1/Normal_posteroanterior_%28PA%29_chest_radiograph_%28X-ray%29.jpg"
            img = load_image_from_url(image_url)

        elif image_source == "Upload Image":
            uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])
            img = load_image_from_upload(uploaded_file)

        else:  # Image URL
            url = st.text_input("Enter image URL:")
            img = load_image_from_url(url) if url else None

        # Display image and controls
        if img:
            st.image(img, caption="Chest X-ray", use_container_width=True)

        else:
            st.info("Please select or upload an image")

# --- REPORT EDITOR ---
with col2:
    with st.container(border=True, height=600):
        report_status_color = "green" if st.session_state.report_status == "Final" else "orange"
        st.subheader(f"📝 Report Editor - [{st.session_state.report_status}]")

        # Initialize empty report content if not exists
        if "report_content" not in st.session_state:
            st.session_state.report_content = ""

        report_height = 480
        if st.session_state.report_generated:
            report_text = st.text_area(
                "Report Content:",
                value=st.session_state.current_report,
                height=report_height,
                key="report_editor"
            )
            # Store the report content in session state
            st.session_state.report_content = report_text
            st.session_state.report_generated = False
        else:
            # Use stored report content or empty string
            report_text = st.text_area(
                "Report Content:",
                value=st.session_state.report_content,
                height=report_height,
                key="report_editor"
            )
            # Update stored report content
            st.session_state.report_content = report_text

        # Add a clear report button
        if st.button("Clear Report"):
            st.session_state.report_content = ""
            st.session_state.report_generated = False
            st.rerun()

# --- AI COPILOT ---
with col3:
    with st.container(border=True, height=600):
        st.subheader("🤖 AI Copilot")

        # Chat messages container
        chat_container = st.container(height=450)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        # Chat input
        if prompt := st.chat_input("💬 Ask me about the X-ray..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            response = process_user_message(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# --- FOOTER ---
with st.container(border=True):
    st.markdown("""
    **Available Commands:**
    • 🔍 `interpret` - Detailed image analysis
    • 📝 `generate report` - Create structured report
    • ⚡ `findings` - Identify key observations
    • ✅ `sign report` - Finalize report
    """)

# --- FOOTER ---
with st.expander("**Expand this container to understand how the agent is reasoning and calling different tools**"):
    with st.chat_message("assistant"):
        st.write("Example of reasoining")
