import pandas as pd

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
