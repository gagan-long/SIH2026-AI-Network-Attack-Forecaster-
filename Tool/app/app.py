import streamlit as st
import pandas as pd
import numpy as np
import os
import tempfile
import tensorflow as tf
import sys
import hashlib
<<<<<<< HEAD
=======
import json
import zipfile
>>>>>>> e5900b2 (doker update pipeline update)

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

<<<<<<< HEAD
=======

def _remove_unsupported_initializer_fields(value):
    unsupported_fields = {
        "input_axes",
        "output_axes",
        "renorm",
        "renorm_clipping",
        "renorm_momentum",
        "quantization_config",
    }
    if isinstance(value, dict):
        return {
            key: _remove_unsupported_initializer_fields(item)
            for key, item in value.items()
            if key not in unsupported_fields
        }
    if isinstance(value, list):
        return [_remove_unsupported_initializer_fields(item) for item in value]
    return value


>>>>>>> e5900b2 (doker update pipeline update)
st.set_page_config(page_title="AI Network Attack Forecaster", page_icon=":material/shield:", layout="wide")
MODEL_PATH = os.path.join(TOOL_ROOT, "models", "saved", "best_world_model.keras")

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] { border-right: 1px solid #d9e2ec; }
        [data-testid="stMetric"] { padding: 0.25rem 0 0.5rem; }
        [data-testid="stExpander"] { border: 1px solid #d9e2ec; border-radius: 6px; }
        h1 { letter-spacing: -0.02em; }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_resource
def load_cached_model():
    if os.path.exists(MODEL_PATH):
        try:
            return tf.keras.models.load_model(MODEL_PATH, compile=False)
<<<<<<< HEAD
        except Exception as e:
            st.sidebar.error(f"Error loading checkpoint: {e}")
=======
        except Exception:
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    compatible_path = os.path.join(temp_dir, "compatible_model.keras")
                    with zipfile.ZipFile(MODEL_PATH) as source, zipfile.ZipFile(compatible_path, "w") as target:
                        for archive_item in source.infolist():
                            content = source.read(archive_item.filename)
                            if archive_item.filename == "config.json":
                                config = json.loads(content.decode("utf-8"))
                                content = json.dumps(
                                    _remove_unsupported_initializer_fields(config)
                                ).encode("utf-8")
                            target.writestr(archive_item, content)
                    return tf.keras.models.load_model(compatible_path, compile=False)
            except Exception as compatibility_error:
                st.sidebar.error(f"Error loading checkpoint: {compatibility_error}")
>>>>>>> e5900b2 (doker update pipeline update)
    return None

model = load_cached_model()

st.sidebar.header("System controls", divider="blue")
if model is not None:
    expected_dim = model.input_shape[-1]
    st.sidebar.success(f"World model active · {expected_dim} features")
else:
    st.sidebar.warning("No checkpoint found · simulation mode")

uploaded_file = st.sidebar.file_uploader("Upload network telemetry (PCAP / CSV, up to 500 MB)", type=["pcap", "csv", "pcapng"])

st.sidebar.subheader("Forecast settings")
K_steps = st.sidebar.slider("Forecast horizon (K)", min_value=3, max_value=20, value=10)
T_length = st.sidebar.slider("Sequence length (T)", min_value=5, max_value=30, value=15)
window_size = st.sidebar.selectbox("Time window", ["5S", "10S", "30S", "1T"], index=1)

st.title("AI network attack forecaster", icon=":material/shield:")
st.caption("Temporal world model for forward infiltration-risk forecasting · SIH 2026")

with st.expander("How it works", icon=":material/info:"):
    st.markdown(
        """
        Upload a PCAP or flow CSV. The pipeline normalizes 32 features, builds a sequence from the latest time windows, and forecasts risk across the next `K` windows.

        Risk is a prioritization signal, not a confirmed incident verdict.
        """
    )

if uploaded_file is not None:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    st.sidebar.info(f"Loaded: `{uploaded_file.name}` ({file_size_mb:.1f} MB)")
    is_pcap = uploaded_file.name.lower().endswith((".pcap", ".pcapng"))
    file_buffer = uploaded_file.getbuffer()
    file_signature = (uploaded_file.name, uploaded_file.size, hashlib.sha1(file_buffer).hexdigest())

    if st.session_state.get("telemetry_signature") != file_signature:
        with st.spinner("Ingesting telemetry and extracting features..."):
            suffix = ".pcap" if is_pcap else ".csv"
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(file_buffer)
                    tmp_path = tmp.name

                if is_pcap:
                    raw_df = extract_pcap_features(tmp_path)
                    df_clean = standardize_dataframe(raw_df)
                    df_clean['Attack_Code'] = 0
                    df_clean['Tactic_Code'] = 0
                else:
                    df_clean = extract_features(tmp_path)
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
            st.session_state.telemetry_signature = file_signature
            st.session_state.telemetry_dataframe = df_clean
            st.session_state.sequence_cache = {}
    else:
        df_clean = st.session_state.telemetry_dataframe

    sequence_key = (file_signature, window_size, T_length)
    if sequence_key not in st.session_state.get("sequence_cache", {}):
        with st.spinner(f"Building {window_size} temporal sequences..."):
            X, _ = build_sequences_pipeline(df_clean, window_size=window_size, T=T_length)
        st.session_state.sequence_cache[sequence_key] = X
    else:
        X = st.session_state.sequence_cache[sequence_key]

    with st.expander("Telemetry diagnostics", icon=":material/monitoring:"):
        c1, c2, c3 = st.columns(3)
        c1.metric("Flows", f"{len(df_clean):,}")
        c2.metric("Sequences", f"{len(X):,}")
        c3.metric("Features", f"{X.shape[-1] if len(X) > 0 else 0} / 32")

    if len(X) == 0:
        st.error("Uploaded capture could not produce valid sequences. Try a smaller window size.")
    else:
        latest_seq = X[-1:] 
        with st.spinner(f"Forecasting {K_steps} windows..."):
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

        col1.metric("Current risk", f"{curr_risk:.1%}")
        col2.metric("Peak risk", f"{max_risk:.1%}", f"+{max_risk - curr_risk:.1%}")
        col3.metric("Lead time", f"+{peak_step} windows")

        st.subheader("Infiltration trajectory")
        st.plotly_chart(plot_risk_timeline(out, threshold=0.75), width="stretch")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Top driving features")
            st.caption("Relative SHAP influence, not attack probability.")
            st.plotly_chart(plot_feature_attribution(out["top_features"]), width="stretch")

        with c2:
            st.subheader("MITRE ATT&CK progression")
            st.caption("Estimated stages, not confirmed labels.")
            st.info(format_mitre_progression(out["tactics"]))
            
            st.subheader("Telemetry snapshot")
            st.caption("Latest normalized records.")
            preview_cols = ['Timestamp', 'Dst Port', 'TotLen Fwd Pkts', 'Port Scan Entropy', 'TCP Retransmission Cnt']
            st.dataframe(df_clean[[c for c in preview_cols if c in df_clean.columns]].tail(6), width="stretch")
else:
    st.info("Upload a PCAP or flow CSV from the sidebar to begin forecasting.", icon=":material/upload_file:")