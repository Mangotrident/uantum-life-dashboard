import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import io
import time

st.set_page_config(page_title="Quantum Life Dashboard", page_icon="🧬", layout="centered")

st.title("🧬 Quantum Life Informatics — QLS Predictor")
st.markdown("Upload your data file to compute and visualize the Quantum Life Score (QLS).")

uploaded_file = st.file_uploader("📂 Upload a data file (.csv or .json)")

if uploaded_file is not None:
    with st.spinner("Uploading and processing..."):
        files = {"file": uploaded_file.getvalue()}
        try:
            response = requests.post(
                "https://uantum-life-dashboard.onrender.com/compute-qls",
                files=files,
                timeout=60
            )
        except Exception as e:
            st.error(f"Connection error: {e}")
            st.stop()

    if response.status_code == 200:
        st.success("✅ Computation complete!")

        # Parse JSON response
        try:
            data = response.json()
        except Exception as e:
            st.error(f"Error parsing response: {e}")
            st.stop()

        # Extract QLS value
        qls_value = data.get("QLS", None)
        if qls_value is not None:
            st.subheader(f"Quantum Life Score (QLS): {qls_value:.3f}")

            # Interpretation
            if qls_value > 0.8:
                interpretation = "🟢 High vitality — system retains strong coherence and adaptive stability."
            elif qls_value > 0.5:
                interpretation = "🟡 Moderate vitality — partial coherence and adaptability."
            else:
                interpretation = "🔴 Low vitality — system rapidly decoheres or becomes inert."
            st.markdown(f"**Interpretation:** {interpretation}")

        # Optional curves if backend returns time-series
        curves = data.get("curves", None)
        if curves:
            df = pd.DataFrame(curves)
            fig = px.line(
                df, x="time", y="qls",
                title="Quantum Life Dynamics",
                labels={"time": "Time", "qls": "Quantum Life Score"}
            )
            st.plotly_chart(fig, use_container_width=True)

            # Download button
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Results (.csv)",
                data=csv,
                file_name="qls_results.csv",
                mime="text/csv"
            )
        else:
            st.json(data)

    else:
        st.error(f"❌ Server returned an error: {response.status_code}")
