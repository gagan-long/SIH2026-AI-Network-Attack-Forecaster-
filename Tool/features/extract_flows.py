import pandas as pd
import numpy as np
from features.canonical_schema import standardize_dataframe

ATTACK_TO_TACTIC = {
    'Benign': 'None',
    'PortScan': 'Reconnaissance',
    'FTP-Patator': 'Initial Access',
    'SSH-Patator': 'Initial Access',
    'Brute Force -Web': 'Initial Access',
    'Brute Force -XSS': 'Initial Access',
    'SQL Injection': 'Initial Access',
    'Infiltration': 'Lateral Movement',
    'Bot': 'C2',
    'DoS attacks-Hulk': 'Impact',
    'DoS attacks-GoldenEye': 'Impact',
    'DoS attacks-Slowloris': 'Impact',
    'DoS attacks-SlowHTTPTest': 'Impact',
    'DDoS attacks-LOIC-HTTP': 'Impact',
    'DDOS attack-HOIC': 'Impact',
    'DDOS attack-LOIC-UDP': 'Impact'
}

def extract_features(file_or_path, nrows=None):
    chunks = pd.read_csv(
        file_or_path,
        nrows=nrows,
        chunksize=100_000,
        low_memory=False,
    )
    normalized_chunks = []

    for chunk in chunks:
        chunk = standardize_dataframe(chunk)
        if 'Label' in chunk.columns:
            chunk['Label'] = chunk['Label'].fillna('Benign')
            chunk['Tactic'] = chunk['Label'].map(ATTACK_TO_TACTIC).fillna('Unknown')
            chunk['Attack_Code'] = chunk['Label'].astype('category').cat.codes
            chunk['Tactic_Code'] = chunk['Tactic'].astype('category').cat.codes
        else:
            chunk['Attack_Code'] = 0
            chunk['Tactic_Code'] = 0
        normalized_chunks.append(chunk)

    if not normalized_chunks:
        return standardize_dataframe(pd.DataFrame()).assign(Attack_Code=0, Tactic_Code=0)
    return pd.concat(normalized_chunks, ignore_index=True)