import streamlit as st
import pandas as pd
import numpy as np
import os
import tempfile
import tensorflow as tf
import sys

TOOL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
for import_root in (TOOL_ROOT, APP_ROOT):
    if import_root not in sys.path:
        sys.path.insert(0, import_root)

from features.extract_flows import extract_features
from features.pcap_extractor import extract_pcap_features
from features.canonical_schema import standardize_dataframe, CANONICAL_32_FEATURES
from features.build_sequences import build_sequences_pipeline
from models.inference import forecast

# Fix import relative path issues
from components import plot_risk_timeline, plot_feature_attribution, format_mitre_progression

st.set_page_config(page_title="AI Network Attack Forecaster", page_icon="🛡️", layout="wide")
MODEL_PATH = os.path.join("models", "saved", "best_world_model.keras")

@st.cache_resource
def load_cached_model():
    if os.path.exists(MODEL_PATH):
        try:
            return tf.keras.models.load_model(MODEL_PATH, compile=False)
        except Exception as e:
            st.sidebar.error(f"Error loading checkpoint: {e}")
    return None

model = load_cached_model()

st.sidebar.header("🛡️ System Controls")
if model is not None:
    expected_dim = model.input_shape[-1]
    st.sidebar.success(f"World Model Active (Expects {expected_dim} Features)")
else:
    st.sidebar.warning("No checkpoint found in models/saved/. Running in Simulation Mode.")

uploaded_file = st.sidebar.file_uploader("Upload Network Telemetry (PCAP / CSV up to 500MB)", type=["pcap", "csv", "pcapng"])

st.sidebar.markdown("### Temporal Parameters")
K_steps = st.sidebar.slider("Forecast Horizon (K steps)", min_value=3, max_value=20, value=10)
T_length = st.sidebar.slider("Sequence Length (T)", min_value=5, max_value=30, value=15)
window_size = st.sidebar.selectbox("Time Window Size", ["5S", "10S", "30S", "1T"], index=1)

st.title("🛡️ AI Network Attack Forecaster")
st.caption("Temporal World Model P(Sₜ₊₁ | Sₜ) & Forward Trajectory Simulation (SIH 2026)")

if uploaded_file is not None:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    st.sidebar.info(f"Loaded: `{uploaded_file.name}` ({file_size_mb:.1f} MB)")
    is_pcap = uploaded_file.name.lower().endswith((".pcap", ".pcapng"))

    with st.spinner(f"Ingesting telemetry and extracting 32 canonical features..."):
        if is_pcap:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pcap") as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name
            raw_df = extract_pcap_features(tmp_path)
            os.remove(tmp_path)
            df_clean = standardize_dataframe(raw_df)
            df_clean['Attack_Code'] = 0
            df_clean['Tactic_Code'] = 0
        else:
            df_clean = extract_features(uploaded_file)

    with st.spinner(f"Resampling into {window_size} windows and stacking temporal sequences..."):
        X, _ = build_sequences_pipeline(df_clean, window_size=window_size, T=T_length)

    with st.expander("🔍 Telemetry Diagnostic Inspector"):
        c1, c2, c3 = st.columns(3)
        c1.write(f"**Total Flows Extracted:** {len(df_clean)}")
        c2.write(f"**Sequence Tensor Shape:** `{X.shape}`")
        c3.write(f"**Active Numeric Features:** {X.shape[-1] if len(X) > 0 else 0} / 32")

    if len(X) == 0:
        st.error("Uploaded capture could not produce valid sequences. Try a smaller window size.")
    else:
        latest_seq = X[-1:] 
        with st.spinner(f"Executing K-Step forward simulation (K={K_steps})..."):
            if model is not None:
                out = forecast(model, latest_seq, K=K_steps, feature_names=CANONICAL_32_FEATURES)
            else:
                base_curve = np.clip(np.linspace(0.18, 0.92, K_steps) + np.random.normal(0, 0.04, K_steps), 0, 1)
                out = {
                    "K": K_steps,
                    "risk_timeline": list(base_curve),
                    "tactics": ["Reconnaissance", "Initial Access", "Lateral Movement", "Lateral Movement", "C2", "C2", "Exfiltration", "Exfiltration", "Impact", "Impact"][:K_steps],
                    "top_features": {"Port Scan Entropy": 0.35, "TCP Retransmission Cnt": 0.28, "TotLen Fwd Pkts": 0.18, "SYN Flag Cnt": 0.11, "Flow IAT Std": 0.08}
                }

        col1, col2, col3 = st.columns(3)
        curr_risk = out["risk_timeline"][0]
        max_risk = max(out["risk_timeline"])
        peak_step = out["risk_timeline"].index(max_risk) + 1

        col1.metric("Current Window Risk", f"{curr_risk:.1%}")
        col2.metric(f"Peak Forecast Risk", f"{max_risk:.1%}", f"+{max_risk - curr_risk:.1%}")
        col3.metric("Defensive Lead Time", f"+{peak_step} Windows Ahead")

        st.markdown("### Forecasted Infiltration Trajectory")
        st.plotly_chart(plot_risk_timeline(out, threshold=0.75), use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Top Driving Features (SHAP Attribution)")
            st.plotly_chart(plot_feature_attribution(out["top_features"]), use_container_width=True)

        with c2:
            st.markdown("### MITRE ATT&CK Stage Progression")
            st.info(format_mitre_progression(out["tactics"]))
            
            st.markdown("### Telemetry Snapshot (Canonical Columns)")
            preview_cols = ['Timestamp', 'Dst Port', 'TotLen Fwd Pkts', 'Port Scan Entropy', 'TCP Retransmission Cnt']
            st.dataframe(df_clean[[c for c in preview_cols if c in df_clean.columns]].tail(6), use_container_width=True)
else:
    st.info("👈 Upload a network capture (PCAP) or flow CSV (up to 500MB) from the sidebar to begin forecasting.")