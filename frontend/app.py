import streamlit as st
import requests
import pandas as pd
import altair as alt
import os
# Base URL of the FastAPI backend the frontend communicates with
# Lets code behave differently depending on where it’s running
# If there's an env var called API_BASE, use it; otherwise, use the default 
API_BASE_DEFAULT = os.getenv("API_BASE", "http://127.0.0.1:8000")

# Maps human-readable chart names in the UI to specific backend API routes
ENDPOINTS = {
    "Patients by condition": "/charts/conditions",
    "Average billing by condition": "/charts/billing-by-conditions",
}

# Cache API responses for 5 minutes to avoid repeatedly sending the same
# file and endpoint request to the backend -> improves performance
@st.cache_data(ttl=300)
def _fetch_endpoint(base_url: str, path: str, file_bytes: bytes, filename: str):

    # Construct full API URL based on user input
    url = f"{base_url.rstrip('/')}{path}"

    # Prepare uploaded CSV file in multipart form format for the API request
    files = {"file": (filename, file_bytes, "text/csv")}

    # Send POST request to backend API
    try:
        resp = requests.post(url, files=files, timeout=60)

    # Handle common network errors
    except requests.Timeout:
        return False, None, "Request timed out."
    except requests.RequestException as e:
        return False, None, f"Request failed: {e!r}"

    # Handle non-200 responses from the backend
    if not resp.ok:
        try:
            body = resp.json()
            detail = body.get("detail")

            # Example: backend validation error (missing dataset columns)
            if isinstance(detail, dict) and "Missing columns" in detail:
                missing = detail["Missing columns"]
                return False, None, f"Missing columns: {', '.join(missing)}"

            if isinstance(detail, str):
                return False, None, detail

            return False, None, resp.text[:500]

        except Exception:
            return False, None, resp.text[:500]

    # Convert API response into JSON data
    try:
        data = resp.json()
    except Exception:
        return False, None, "Response was not valid JSON."

    return True, data, None


def build_chart_conditions(data: list) -> alt.Chart | None:

    # Convert API JSON response into a Pandas DataFrame
    df = pd.DataFrame(data)

    # Validate that expected columns exist
    if df.empty or "condition" not in df.columns or "count" not in df.columns:
        return None

    # Ensure counts are numeric and replace invalid values
    df["count"] = pd.to_numeric(df["count"], errors="coerce").fillna(0)

    # Sort and select top 30 conditions for visualization
    df = df.sort_values("count", ascending=True).tail(30)

    # Build Altair bar chart showing patient count per condition
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("count:Q", title="Patients"),
            y=alt.Y("condition:N", sort="-x", title="Condition"),
        )
        .properties(height=400)
    )


def build_chart_billing(data: list) -> alt.Chart | None:

    # Convert API output to DataFrame
    df = pd.DataFrame(data)

    col_cond = "Medical Condition"
    col_billing = "Mean Billing Amount"

    # Validate fields returned by backend
    if df.empty or col_cond not in df.columns or col_billing not in df.columns:
        return None

    # Convert billing values to numeric format
    df[col_billing] = pd.to_numeric(df[col_billing], errors="coerce")

    # Remove invalid values and select top 30
    df = df.dropna(subset=[col_billing]).sort_values(col_billing, ascending=True).tail(30)

    # Build chart showing average billing per medical condition
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(col_billing + ":Q", title="Mean billing ($)"),
            y=alt.Y(col_cond + ":N", sort="-x", title="Condition"),
        )
        .properties(height=400)
    )


# Add Streamlit page layout and title
st.set_page_config(page_title="Clinical Data Pipeline", layout="wide")

# Main app title
st.title("Clinical Data Pipeline")

# Sidebar UI allows users to configure API endpoint and backend URL
with st.sidebar:
    st.subheader("Controls")

    # Allows switching backend environments if needed
    api_base = st.text_input("API base URL", value=API_BASE_DEFAULT)

    # Dropdown to select which chart endpoint to call
    chart_endpoint = st.selectbox(
        "Endpoint to visualize",
        options=["— None —"] + list(ENDPOINTS.keys()),
    )


# File uploader lets users submit a CSV dataset to the backend
file = st.file_uploader("Please upload CSV file", type=["csv"])

if file is not None:

    # Display uploaded file name
    st.write("Filename:", file.name)

    # Send file to preview endpoint which calculates dataset summary statistics
    response = requests.post(
        f"{API_BASE_DEFAULT}/upload/preview",
        files={"file": file}
    )

    if response.status_code == 200:
        data = response.json()

        st.success("File processed")

        # Display basic dataset information returned by backend
        if "rows" in data and "cols" in data:
            st.write("Rows:", data["rows"])
            st.write("Columns:", data["cols"])

        # Display computed summary statistics
        if "avg_age" in data:
            st.write("Average Age:", round(data["avg_age"], 2))

        if "avg_stay_length" in data:
            st.write("Average Length of Stay:", round(data["avg_stay_length"], 2))

        # Show first few rows of the dataset
        if "head" in data:
            st.dataframe(data["head"])

    else:
        # Display backend error response
        st.error("API Error")
        st.write(response.text)


# If user selects a chart endpoint, call backend and render charts
if file is not None and chart_endpoint and chart_endpoint != "— None —":

    path = ENDPOINTS.get(chart_endpoint)

    if path:
        st.subheader(f"Chart: {chart_endpoint}")

        # Convert uploaded file into raw bytes for API request
        file_bytes = file.getvalue()

        ok, data, err = _fetch_endpoint(api_base, path, file_bytes, file.name)

        if not ok:
            st.error(err)

        else:
            # Build the correct chart depending on which endpoint was selected
            if chart_endpoint == "Patients by condition":
                chart = build_chart_conditions(data)
            else:
                chart = build_chart_billing(data)

            # Render chart in Streamlit
            if chart is not None:
                st.altair_chart(chart, use_container_width=True)

            # Display raw API response data as a table
            df = pd.DataFrame(data) if data else pd.DataFrame()
            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)