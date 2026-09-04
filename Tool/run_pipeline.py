import argparse
import os
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description="SIH 2026: AI Network Attack Forecaster Pipeline")
    parser.add_argument('--action', choices=['generate', 'train', 'evaluate', 'demo', 'all'], required=True,
                        help="Action to perform: generate (data), train (model), evaluate (baseline), demo (UI), or all.")
    
    args = parser.parse_args()

    # 1. Generate Synthetic Data
    if args.action in ['generate', 'all']:
        print("\n[>>>] STEP 1: Generating Synthetic Multi-Stage PCAP...")
        subprocess.run([sys.executable, "scripts/generate_synthetic_pcap.py"], check=True)

    # 2. Train World Model
    if args.action in ['train', 'all']:
        print("\n[>>>] STEP 2: Training CNN-BiLSTM World Model...")
        train_script = """
from features.pcap_extractor import extract_pcap_features
from features.build_sequences import build_sequences_pipeline
from models.world_model import build_world_model
from models.train import train_world_model

print('Extracting features from synthetic PCAP...')
df = extract_pcap_features('data/raw/synthetic_multi_stage_attack.pcap')
df['Attack_Code'] = 0
df['Tactic_Code'] = 0

print('Building sequences...')
X, y = build_sequences_pipeline(df, window_size='10S', T=15)

if len(X) > 0:
    print('Building and training World Model...')
    model = build_world_model(sequence_length=15, feature_dim=X.shape[-1], num_attack_classes=16, num_tactic_classes=7)
    train_world_model(X, y, X, y, model, epochs=5, batch_size=32)
else:
    print('Not enough data to train. Please generate more traffic.')
        """
        subprocess.run([sys.executable, "-c", train_script], check=True)

    # 3. Evaluate Baseline
    if args.action in ['evaluate', 'all']:
        print("\n[>>>] STEP 3: Evaluating Logistic Regression Baseline...")
        subprocess.run([sys.executable, "-m", "baseline.logistic_regression"], check=True)

    # 4. Launch Streamlit UI
    if args.action in ['demo', 'all']:
        print("\n[>>>] STEP 4: Launching Offline Streamlit Dashboard (500MB Upload Enabled)...")
        subprocess.run([
            "streamlit", "run", "app/app.py", 
            "--server.maxUploadSize=500",
            "--server.port=8501"
        ], check=True)

if __name__ == "__main__":
    main()