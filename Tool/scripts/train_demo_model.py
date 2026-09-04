# scripts/train_demo_model.py
import os
import sys

# Ensure the root directory is in the Python path for relative imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from features.pcap_extractor import extract_pcap_features
from features.canonical_schema import standardize_dataframe
from features.build_sequences import build_sequences_pipeline
from models.world_model import build_world_model
from models.train import train_world_model
from scripts.generate_synthetic_pcap import generate_multi_stage_pcap

def main():
    print("==================================================")
    print("🚀 : AI Network Attack Forecaster Training")
    print("==================================================")

    # 1. Generate Training Data
    pcap_path = 'data/raw/synthetic_multi_stage_attack.pcap'
    if not os.path.exists(pcap_path):
        print("\n[1/4] Generating synthetic multi-stage attack PCAP...")
        generate_multi_stage_pcap(pcap_path)
    else:
        print("\n[1/4] Using existing synthetic PCAP dataset.")

    # 2. Extract Features
    print("\n[2/4] Extracting raw packet features via Scapy...")
    raw_df = extract_pcap_features(pcap_path)
    
    # Standardize and add mock labels for the demo dataset
    df_clean = standardize_dataframe(raw_df)
    
    # We inject synthetic labels so the focal loss has targets to train on.
    # In a real scenario (like CIC-IDS2018), these come from the dataset.
    df_clean['Attack_Code'] = (df_clean['Port Scan Entropy'] > 1.0).astype(int) 
    df_clean['Tactic_Code'] = (df_clean['TCP Retransmission Cnt'] > 2).astype(int) 

    # 3. Build Sequences
    print("\n[3/4] Building temporal sequences (T=15)...")
    X, y_dict = build_sequences_pipeline(df_clean, window_size='10S', T=15)
    
    if len(X) < 10:
        print("[ERROR] Not enough data sequences generated to train. Please increase PCAP length.")
        return

    # 4. Model Training
    print("\n[4/4] Instantiating and training the CNN-BiLSTM World Model...")
    
    # Dynamically grab the dimension to ensure alignment
    feature_dim = X.shape[-1]
    
    model = build_world_model(
        sequence_length=15, 
        feature_dim=feature_dim, 
        num_attack_classes=16, 
        num_tactic_classes=7
    )
    
    # In a real environment, you would split X and y into train/val. 
    # For this demo script, we use the same data for both to ensure it compiles.
    train_world_model(
        X_train=X, y_train_dict=y_dict,
        X_val=X, y_val_dict=y_dict,
        model=model, epochs=5, batch_size=16
    )

if __name__ == "__main__":
    main()