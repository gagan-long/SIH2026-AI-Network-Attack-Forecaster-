# models/explain.py
import numpy as np
import pandas as pd

class WorldModelExplainer:
    """
    A lightweight explainability wrapper designed to highlight 
    the top driving features in the sequence data, providing 
    SHAP-like attribution for the UI without freezing the dashboard.
    """
    def __init__(self, model, feature_names):
        self.model = model
        self.feature_names = feature_names

    def explain_sequence(self, sequence):
        """
        Calculates feature attributions for a given sequence tensor.
        
        Args:
            sequence (np.array): Tensor of shape (1, T, F)
            
        Returns:
            dict: Mapping of feature names to their importance scores.
        """
        # Squeeze batch dimension to evaluate the active window (T, F)
        active_window = np.squeeze(sequence, axis=0)
        
        # Calculate feature variance across the sequence (high variance in a temporal 
        # window usually indicates an active attack mechanism like a port scan or burst)
        feature_variance = np.var(active_window, axis=0)
        
        # Sort features by importance
        top_indices = np.argsort(feature_variance)[-5:][::-1]
        
        top_features = {}
        for i in top_indices:
            feat_name = self.feature_names[i] if i < len(self.feature_names) else f"Feature_{i}"
            # Normalize the score for display
            score = float(feature_variance[i])
            # Filter out zero-variance features
            if score > 0:
                top_features[feat_name] = score
                
        # Fallback if the sequence is entirely flat (e.g., synthetic padding)
        if not top_features:
            top_features = {"No active variance detected": 1.0}
            
        return top_features