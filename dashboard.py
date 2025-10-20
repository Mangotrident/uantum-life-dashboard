import os
from train_model import train_and_save_model

if not os.path.exists("model.pkl"):
    st.warning("Training model from embedded Phase 3 pipeline... please wait ⏳")
    train_and_save_model("phase2_benchmark_results.csv")
    st.success("Model rebuilt successfully ✅")

import json, joblib, pandas as pd, numpy as np
import streamlit as st

st.set_page_config(page_title="Quantum Life Informatics", layout="centered")
st.title("🧬 Quantum Life Informatics — QLS Predictor")

@st.cache_resource(show_spinner=False)
def load_bundle():
    model = joblib.load("model.pkl")               # Phase 3/5 model
    with open("metadata.json") as f:
        meta = json.load(f)
    # bounds fallback if missing
    b = meta.get("bounds", {"J":[0.05,0.4], "gamma":[0.005,0.05], "sigma":[0.0,0.08]})
    width = float(meta.get("conformal_width_90", 0.15))
    topos = meta.get("topologies_seen", ["line","ring","smallworld"])
    return model, b, width, topos

try:
    pipe, bounds, width, topos = load_bundle()
    st.success("Model loaded.")
except Exception as e:
    st.error(f"Could not load model/metadata: {e}")
    st.stop()

# UI
topology = st.selectbox("Topology", topos)
J     = st.slider("Coupling J",     float(bounds["J"][0]),     float(bounds["J"][1]),     float(np.mean(bounds["J"])),     0.005)
gamma = st.slider("Dephasing γ",    float(bounds["gamma"][0]), float(bounds["gamma"][1]), float(np.mean(bounds["gamma"])), 0.001)
sigma = st.slider("Static disorder σ", float(bounds["sigma"][0]), float(bounds["sigma"][1]), float(np.mean(bounds["sigma"])), 0.002)

if st.button("Predict QLS", type="primary"):
    X = pd.DataFrame([{"topology": topology, "J": J, "gamma": gamma, "sigma": sigma}])
    y = float(pipe.predict(X)[0])
    lo, hi = y - width, y + width
    st.metric("Predicted QLS", f"{y:.4f}")
    st.caption(f"90% prediction interval: [{lo:.4f}, {hi:.4f}]")

with st.expander("Optional: Recalibrate uncertainty from a CSV (Phase 2 results)"):
    up = st.file_uploader("Upload phase2_benchmark_results.csv", type=["csv"])
    if up is not None:
        try:
            df = pd.read_csv(up)
            df = df.dropna(subset=["topology","J","gamma","sigma"])
            yhat = pipe.predict(df[["topology","J","gamma","sigma"]])
            if "QLS" in df.columns:
                resid = np.abs(df["QLS"].to_numpy() - yhat)
            else:
                resid = np.abs(yhat - np.median(yhat))
            new_w = float(np.quantile(resid, 0.9))
            st.success(f"Recalibrated 90% width = {new_w:.4f} (session only)")
            width = new_w
        except Exception as e:
            st.error(f"Could not recalibrate: {e}")
