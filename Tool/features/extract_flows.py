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
    df = pd.read_csv(file_or_path, nrows=nrows, low_memory=False)
    df = standardize_dataframe(df)

    if 'Label' in df.columns:
        df['Label'] = df['Label'].fillna('Benign')
        df['Tactic'] = df['Label'].map(ATTACK_TO_TACTIC).fillna('Unknown')
        df['Attack_Code'] = df['Label'].astype('category').cat.codes
        df['Tactic_Code'] = df['Tactic'].astype('category').cat.codes
    else:
        df['Attack_Code'] = 0
        df['Tactic_Code'] = 0

    return df