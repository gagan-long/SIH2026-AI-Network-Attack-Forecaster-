import os
import tensorflow as tf
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

class SparseCategoricalFocalLoss(tf.keras.losses.Loss):
    """
    Custom Sparse Focal Loss to handle severe class imbalance.
    Formula: FL(p_t) = -alpha * (1 - p_t)^gamma * log(p_t)
    """
    def __init__(self, gamma=2.0, alpha=0.25, name='sparse_categorical_focal_loss', **kwargs):
        super().__init__(name=name, **kwargs)
        self.gamma = gamma
        self.alpha = alpha

    def call(self, y_true, y_pred):
        # Ensure y_pred is bounded to avoid log(0)
        y_pred = tf.clip_by_value(y_pred, tf.keras.backend.epsilon(), 1.0 - tf.keras.backend.epsilon())
        
        # Gather the probabilities of the true classes
        y_true = tf.cast(tf.squeeze(y_true), dtype=tf.int32)
        
        # Calculate cross entropy
        cross_entropy = tf.keras.losses.sparse_categorical_crossentropy(y_true, y_pred)
        
        # Get the predicted probability for the true class to calculate the focal weight
        p_t = tf.gather(y_pred, y_true, batch_dims=1)
        focal_weight = self.alpha * tf.pow(1.0 - p_t, self.gamma)
        
        return focal_weight * cross_entropy

def train_world_model(X_train, y_train_dict, X_val, y_val_dict, model, epochs=50, batch_size=64):
    """
    Compiles and trains the multi-task World Model.
    
    Args:
        X_train (np.array): Training sequences of shape (Batch, T, 32).
        y_train_dict (dict): Dictionary with keys 'state', 'attack', 'tactic'.
        X_val (np.array): Validation sequences.
        y_val_dict (dict): Validation targets.
        model (tf.keras.Model): The built World Model.
        epochs (int): Max training epochs.
        batch_size (int): Batch size.
    """
    print("\n[INFO] Compiling World Model with Multi-Task Loss...")
    
    # Define the losses for each head
    losses = {
        'state': 'mse',                                      # Mean Squared Error for continuous features
        'attack': SparseCategoricalFocalLoss(gamma=2.0),     # Focal loss for imbalanced signatures
        'tactic': SparseCategoricalFocalLoss(gamma=2.0)      # Focal loss for imbalanced MITRE stages
    }
    
    # Weight the losses (Prioritize tactic and attack classification over perfect state reconstruction)
    loss_weights = {
        'state': 0.3,
        'attack': 1.0,
        'tactic': 1.0
    }
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss=losses,
        loss_weights=loss_weights,
        metrics={
            'state': ['mae'],
            'attack': ['accuracy'],
            'tactic': ['accuracy']
        }
    )
    
    # Create the save directory if it doesn't exist
    save_dir = os.path.join("models", "saved")
    os.makedirs(save_dir, exist_ok=True)
    checkpoint_path = os.path.join(save_dir, "best_world_model.keras")
    
    # Define Callbacks
    callbacks = [
        ModelCheckpoint(
            filepath=checkpoint_path,
            monitor='val_tactic_loss', # Save the model that generalizes MITRE tactics best
            save_best_only=True,
            verbose=1
        ),
        EarlyStopping(
            monitor='val_tactic_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            verbose=1
        )
    ]
    
    print("\n[INFO] Starting Training Loop...")
    history = model.fit(
        X_train, 
        {'state': y_train_dict['state'], 'attack': y_train_dict['attack'], 'tactic': y_train_dict['tactic']},
        validation_data=(X_val, {'state': y_val_dict['state'], 'attack': y_val_dict['attack'], 'tactic': y_val_dict['tactic']}),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1
    )
    
    print(f"\n[SUCCESS] Training complete. Best model saved to: {checkpoint_path}")
    return history