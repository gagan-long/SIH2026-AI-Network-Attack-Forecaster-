import numpy as np
import pandas as pd

# The 32 standard features (Flow-level + Packet-level)
CANONICAL_32_FEATURES = [
    'Dst Port', 'Protocol', 'Flow Duration', 'Tot Fwd Pkts', 'Tot Bwd Pkts',
    'TotLen Fwd Pkts', 'TotLen Bwd Pkts', 'Fwd Pkt Len Max', 'Fwd Pkt Len Min',
    'Fwd Pkt Len Mean', 'Fwd Pkt Len Std', 'Bwd Pkt Len Max', 'Bwd Pkt Len Min',
    'Bwd Pkt Len Mean', 'Bwd Pkt Len Std', 'Flow Byts/s', 'Flow Pkts/s',
    'Flow IAT Mean', 'Flow IAT Std', 'Fwd IAT Mean', 'Bwd IAT Mean',
    'FIN Flag Cnt', 'SYN Flag Cnt', 'RST Flag Cnt', 'PSH Flag Cnt',
    'ACK Flag Cnt', 'URG Flag Cnt', 'Down/Up Ratio', 'TTL Mean',
    'TTL Variance', 'Port Scan Entropy', 'TCP Retransmission Cnt'
]

HEADER_ALIASES = {
    'dst_port': 'Dst Port', 'destination port': 'Dst Port', 'dport': 'Dst Port',
    'proto': 'Protocol', 'flow_duration': 'Flow Duration', 'tot fwd pkts': 'Tot Fwd Pkts',
    'total fwd packets': 'Tot Fwd Pkts', 'tot bwd pkts': 'Tot Bwd Pkts',
    'total backward packets': 'Tot Bwd Pkts', 'totlen fwd pkts': 'TotLen Fwd Pkts',
    'total length of fwd packets': 'TotLen Fwd Pkts', 'totlen bwd pkts': 'TotLen Bwd Pkts',
    'total length of bwd packets': 'TotLen Bwd Pkts', 'flow byts/s': 'Flow Byts/s',
    'flow bytes/s': 'Flow Byts/s', 'flow pkts/s': 'Flow Pkts/s',
    'flow packets/s': 'Flow Pkts/s', 'flow iat mean': 'Flow IAT Mean',
    'flow iat std': 'Flow IAT Std', 'fin flag cnt': 'FIN Flag Cnt',
    'syn flag cnt': 'SYN Flag Cnt', 'rst flag cnt': 'RST Flag Cnt',
    'psh flag cnt': 'PSH Flag Cnt', 'ack flag cnt': 'ACK Flag Cnt',
    'urg flag cnt': 'URG Flag Cnt', 'down/up ratio': 'Down/Up Ratio',
    'source ip': 'Src IP', 'srcip': 'Src IP', 'src_ip': 'Src IP',
    'timestamp': 'Timestamp', 'time': 'Timestamp'
}

def standardize_dataframe(df):
    df = df.copy()
    cleaned_cols = {}
    for col in df.columns:
        norm_key = str(col).strip().lower()
        cleaned_cols[col] = HEADER_ALIASES.get(norm_key, str(col).strip())
    df.rename(columns=cleaned_cols, inplace=True)

    if 'Timestamp' not in df.columns:
        df['Timestamp'] = pd.date_range(start='2026-01-01', periods=len(df), freq='100ms')
    else:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='mixed', errors='coerce')
        fallback_timestamps = pd.Series(
            pd.date_range(start='2026-01-01', periods=len(df), freq='100ms'),
            index=df.index,
        )
        df['Timestamp'] = df['Timestamp'].fillna(fallback_timestamps)

    if 'Src IP' not in df.columns:
        df['Src IP'] = '192.168.1.100'

    for feat in CANONICAL_32_FEATURES:
        if feat in df.columns:
            df[feat] = pd.to_numeric(df[feat], errors='coerce')
        else:
            df[feat] = 0.0

    df = df.replace([np.inf, -np.inf], np.nan)
    df[CANONICAL_32_FEATURES] = df[CANONICAL_32_FEATURES].fillna(0.0)

    reserved = ['Timestamp', 'Src IP', 'Label', 'Attack_Code', 'Tactic_Code']
    keep_cols = [c for c in reserved if c in df.columns] + CANONICAL_32_FEATURES
    return df[keep_cols]