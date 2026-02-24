import streamlit as st
import requests

st.title("Clinical Data Pipeline")

file = st.file_uploader("Please upload CSV file", type=["csv"])

if file is not None:
    st.write("Filename:", file.name)

    response = requests.post(
        "http://127.0.0.1:8000/upload/preview",
        files={"file": file}
    )

    if response.status_code == 200:
        data = response.json()

        st.success("File processed")

        if "rows" in data and "cols" in data:
            st.write("Rows:", data["rows"])
            st.write("Columns:", data["cols"])

        if "avg_age" in data:
            st.write("Average Age:", round(data["avg_age"], 2))

        if "avg_stay_length" in data:
            st.write("Average Length of Stay:", round(data["avg_stay_length"], 2))

        if "head" in data:
            st.dataframe(data["head"])
    else:
        st.error("API Error")
        st.write(response.text)