import streamlit as st
import json
import constants as c

def open_new_case(case_number: int) -> bool:
    """
    This function open a new case. At the end, it will return True if it was successful, False otherwise.

    :param case_number: int
    :return: bool
    """

    for idx, row in st.session_state.cases_df.iterrows():
        if idx == case_number:
            st.session_state.image_url = c.SAMPLE_CASES[idx]
            st.session_state["history"].append(
                {"user_message": None,
                 "assistant_message": f"📋 Now viewing {row['Patient ID']}. How can I assist you?",
                 "reasoning": None})
            st.session_state.report_text = ""
            st.rerun()

            return json.dumps(True)

    return False
