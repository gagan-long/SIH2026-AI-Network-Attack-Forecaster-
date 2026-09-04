import tensorflow as tf
from tensorflow.keras import layers, Model

def build_world_model(sequence_length=15, feature_dim=32, num_attack_classes=16, num_tactic_classes=7):
    """
    Builds the Multi-Task CNN-BiLSTM World Model.
    
    Args:
        sequence_length (int): The number of time windows in each sequence (T).
        feature_dim (int): The number of features per window (F).
        num_attack_classes (int): Number of specific attack signatures.
        num_tactic_classes (int): Number of MITRE ATT&CK tactics.
        
    Returns:
        tf.keras.Model: The compiled, untrained World Model.
    """
    # Input sequence of shape (Batch, T, F)
    inputs = layers.Input(shape=(sequence_length, feature_dim), name="sequence_input")
    
    # ---------------------------------------------------------
    # Spatial/Local Feature Extraction (CNN)
    # ---------------------------------------------------------
    # Extracts local micro-bursts (e.g., sudden port scan spikes)
    x = layers.Conv1D(filters=64, kernel_size=3, padding='same', activation='relu')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Conv1D(filters=128, kernel_size=3, padding='same', activation='relu')(x)
    x = layers.BatchNormalization()(x)
    
    # ---------------------------------------------------------
    # Temporal Dynamics Modeling (BiLSTM)
    # ---------------------------------------------------------
    # Captures long-range causal dependencies (e.g., Recon -> Latency -> Exploit)
    x = layers.Bidirectional(layers.LSTM(128, return_sequences=False))(x)
    x = layers.Dropout(0.3)(x)
    
    # Shared Latent Representation (The "Environment" State)
    shared_latent = layers.Dense(128, activation='relu', name="shared_latent")(x)
    shared_latent = layers.BatchNormalization()(shared_latent)
    
    # ---------------------------------------------------------
    # Multi-Task Prediction Heads
    # ---------------------------------------------------------
    
    # Head 1: State Dynamics (Predicts the physical features of step T+1)
    # Uses linear activation because features are continuous numerical values
    state_out = layers.Dense(feature_dim, activation='linear', name='state')(shared_latent)
    
    # Head 2: Attack Classification (Specific exploit signature)
    attack_out = layers.Dense(num_attack_classes, activation='softmax', name='attack')(shared_latent)
    
    # Head 3: MITRE ATT&CK Tactic Classification (The high-level kill chain stage)
    tactic_out = layers.Dense(num_tactic_classes, activation='softmax', name='tactic')(shared_latent)
    
    # Compile Model Structure
    model = Model(inputs=inputs, outputs=[state_out, attack_out, tactic_out], name="WorldModel_CNN_BiLSTM")
    
    return model