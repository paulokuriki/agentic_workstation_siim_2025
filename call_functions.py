import streamlit as st
import json

def load_case(case_number: int) -> str:
    """
    Opens a new case in the workstation by updating Streamlit session state.

    :param case_number: The index of the case to open.
    :return: A JSON string of "True" if loading was successful, or "False" otherwise.
    """
    for idx, row in st.session_state.cases_df.iterrows():
        if row["id"] == case_number:
            # Update session state
            st.session_state.image_url = row["url"]
            st.session_state["history"].append(
                {
                    "user_message": None,
                    "assistant_message": f"📋 Now viewing {row['id']}. How can I assist you?",
                    "reasoning": None
                }
            )
            st.session_state.report_text = ""

            return json.dumps(True)

    return json.dumps(False)

def list_available_cases() -> str:
    """
    This function extracts all the case IDs and returns them as a list.

    :return: A JSON string of a list of integers representing available case IDs.
    """

    cases_id = json.dumps(st.session_state.cases_df.id.to_list())
    return cases_id