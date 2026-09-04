# scripts/prepare_dataset.py
import os
import sys
import pandas as pd
import numpy as np

# Ensure the root directory is in the Python path for relative imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from features.extract_flows import extract_features
from features.build_sequences import build_sequences_pipeline

def prepare_cic_dataset(raw_csv_path, output_dir, window_size='10S', T=15):
    print("==================================================")
    print("⚙️ Preparing CIC-IDS2018 Dataset for World Model")
    print("==================================================")
    
    if not os.path.exists(raw_csv_path):
        print(f"[ERROR] Raw dataset not found at {raw_csv_path}")
        print("Please download '02-28-2018.csv' (or similar) into the data/ directory.")
        return

    print(f"[1/4] Loading raw telemetry from {raw_csv_path}...")
    # Load and clean through the canonical standardizer
    df_clean = extract_features(raw_csv_path)
    
    print(f"      Total flows extracted: {len(df_clean)}")
    print(f"      Attack composition:\n{df_clean['Tactic'].value_counts()}")

    # ---------------------------------------------------------
    # Downsample Benign Traffic for Balance
    # ---------------------------------------------------------
    print("\n[2/4] Balancing classes (Downsampling Benign traffic)...")
    df_malicious = df_clean[df_clean['Tactic'] != 'None']
    df_benign = df_clean[df_clean['Tactic'] == 'None']
    
    # Cap benign traffic to roughly 2x the size of malicious traffic to maintain temporal gaps
    # but prevent extreme 99:1 imbalance
    target_benign_count = min(len(df_benign), len(df_malicious) * 2)
    
    if target_benign_count > 0 and len(df_malicious) > 0:
        df_benign_sampled = df_benign.sample(n=target_benign_count, random_state=42)
        df_balanced = pd.concat([df_benign_sampled, df_malicious]).sort_values('Timestamp')
    else:
        df_balanced = df_clean

    print(f"      Balanced flows count: {len(df_balanced)}")

    # ---------------------------------------------------------
    # Sequence Generation
    # ---------------------------------------------------------
    print(f"\n[3/4] Generating Temporal Sequences (Window={window_size}, T={T})...")
    X, y_dict = build_sequences_pipeline(df_balanced, window_size=window_size, T=T)
    
    if len(X) == 0:
        print("[ERROR] Failed to generate sequences. Dataset might be too small after filtering.")
        return

    # ---------------------------------------------------------
    # Save Processed Tensors
    # ---------------------------------------------------------
    print("\n[4/4] Saving processed tensors to disk...")
    os.makedirs(output_dir, exist_ok=True)
    
    np.save(os.path.join(output_dir, "X_train.npy"), X)
    np.save(os.path.join(output_dir, "y_state.npy"), y_dict['state'])
    np.save(os.path.join(output_dir, "y_attack.npy"), y_dict['attack'])
    np.save(os.path.join(output_dir, "y_tactic.npy"), y_dict['tactic'])
    
    print(f"[SUCCESS] Tensors saved to {output_dir}")
    print(f"          X Shape: {X.shape}")

if __name__ == "__main__":
    raw_path = os.path.join("data", "02-28-2018.csv")
    out_path = os.path.join("data", "processed")
    prepare_cic_dataset(raw_path, out_path)