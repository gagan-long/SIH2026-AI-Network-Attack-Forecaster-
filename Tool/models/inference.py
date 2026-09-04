import numpy as np
import tensorflow as tf

TACTIC_CLASSES = [
    'None', 'Reconnaissance', 'Initial Access', 
    'Lateral Movement', 'C2', 'Impact', 'Exfiltration'
]

TACTIC_RISK_WEIGHTS = {
    'None': 0.00, 'Reconnaissance': 0.20, 'Initial Access': 0.50,
    'Lateral Movement': 0.85, 'C2': 0.90, 'Impact': 0.80, 'Exfiltration': 1.00
}

def calculate_risk_score(tactic_probs):
    risk = sum(prob * TACTIC_RISK_WEIGHTS.get(TACTIC_CLASSES[i], 0.0) 
               for i, prob in enumerate(tactic_probs) if i < len(TACTIC_CLASSES))
    return float(min(risk, 1.0))

def forecast(model, sequence, K=10, feature_names=None):
    if len(sequence.shape) == 2:
        current_seq = np.expand_dims(sequence, axis=0)
    else:
        current_seq = sequence.copy()

    expected_dim = model.input_shape[-1]
    actual_dim = current_seq.shape[-1]

    if actual_dim != expected_dim:
        if actual_dim < expected_dim:
            pad_width = ((0, 0), (0, 0), (0, expected_dim - actual_dim))
            current_seq = np.pad(current_seq, pad_width, mode='constant', constant_values=0)
        else:
            current_seq = current_seq[:, :, :expected_dim]

    risk_timeline = []
    predicted_tactics = []

    for _ in range(K):
        preds = model.predict(current_seq, verbose=0)
        next_state_pred = preds[0]
        tactic_probs = preds[2][0]

        step_risk = calculate_risk_score(tactic_probs)
        dominant_idx = int(np.argmax(tactic_probs))
        dominant_tactic = TACTIC_CLASSES[dominant_idx] if dominant_idx < len(TACTIC_CLASSES) else "Unknown"

        risk_timeline.append(step_risk)
        predicted_tactics.append(dominant_tactic)

        next_state_reshaped = np.expand_dims(next_state_pred, axis=1)
        current_seq = np.concatenate([current_seq[:, 1:, :], next_state_reshaped], axis=1)

    variances = np.var(current_seq[0], axis=0)
    top_indices = np.argsort(variances)[-5:][::-1]
    top_features = {
        (feature_names[i] if feature_names and i < len(feature_names) else f"Feature_{i}"): float(variances[i])
        for i in top_indices
    }

    return {
        "K": K,
        "risk_timeline": risk_timeline,
        "tactics": predicted_tactics,
        "top_features": top_features
    }