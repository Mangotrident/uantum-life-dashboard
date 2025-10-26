import streamlit as st
import requests

st.title("Quantum Life Dashboard")

uploaded_file = st.file_uploader("Upload a data file to compute QLS")

if uploaded_file is not None:
    with st.spinner("Processing..."):
        files = {"file": uploaded_file.getvalue()}
        response = requests.post(
            "https://uantum-life-dashboard.onrender.com/compute-qls",
            files=files
        )
    
    if response.status_code == 200:
        st.success("Computation complete!")
        st.json(response.json())
    else:
        st.error(f"Error: {response.status_code}")
