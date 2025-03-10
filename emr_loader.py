import pandas as pd
import streamlit as st

from constants import CASES


def search_records(search_type: str, search_field: str) -> pd.DataFrame:
    """Search records by Study ID or Patient MRN, returning either reports or a flattened chart view."""
    df = pd.DataFrame(CASES)

    # 1) Narrow down the matches
    if search_type == "Study ID":
        result_df = df[df["Study ID"].astype(str).str.contains(search_field, case=False, na=False)]
    elif search_type == "Patient MRN":
        result_df = df[df["Patient MRN"].str.contains(search_field, case=False, na=False)]
    else:
        return pd.DataFrame()  # No valid search

    if result_df.empty:
        return pd.DataFrame()  # No matches

    # 2) If searching by Study ID → return the "report" rows
    if search_type == "Study ID":
        # Just return top-level columns
        return result_df[
            ["Study ID", "Patient MRN", "Date", "Modality"]].reset_index(drop=True)

    # 3) If searching by Patient MRN → flatten & return the medical charts
    if search_type == "Patient MRN":
        expanded_rows = []
        for _, row in result_df.iterrows():
            for chart_item in row["medical_charts"]:
                flattened = {"Patient MRN": row["Patient MRN"]}
                # Merge this particular chart entry
                flattened.update(chart_item)
                expanded_rows.append(flattened)
        return pd.DataFrame(expanded_rows).reset_index(drop=True)

    # Fallback — should never be reached if you covered all search types
    return pd.DataFrame()


def get_clinical_data_from_patient():
    """
    Retrieves and formats clinical data for a specific patient based on the selected study ID.

    This function searches for a matching study ID and extracts the associated medical charts.
    The data is formatted into a markdown string for easy presentation.

    Args:
        None

    Returns:
        str: A markdown-formatted string containing clinical data details including:
            - Date of visit
            - Reason for visit
            - Patient history
            - Vitals
            - Diagnosis
            - Treatment
            - Assessment
            - Plan
            - Findings
            - Recommendations

        If no matching data is found, the message "No data was found" will be returned.
    """
    df = pd.DataFrame(CASES)

    if "study_id" in st.session_state:
        study_id = st.session_state["study_id"]
    else:
        study_id = 0

    # Step 1: Identify the patient using study_id
    patient_data = df[df["Study ID"] == study_id]

    if patient_data.empty:
        return "No data was found"

    # Step 2: Extract and sort medical charts by date (descending)
    medical_charts = []
    for _, row in patient_data.iterrows():
        if "medical_charts" in row:
            medical_charts.extend(row["medical_charts"])

    if not medical_charts:
        return "No clinical data available for this patient"

    # Step 3: Sort charts by date (newest first)
    medical_charts = sorted(medical_charts, key=lambda x: x['Date'], reverse=True)

    # Step 4: Build a Markdown string dynamically from available fields
    response = f"## Clinical Data for Study ID: {study_id}\n"
    for chart in medical_charts:
        response += f"### Date: {chart['Date']}\n"
        for key, value in chart.items():
            if key != 'Date' and pd.notna(value) and value:
                response += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        response += "\n"

    return response
