import pandas as pd
import numpy as np
from features.canonical_schema import CANONICAL_32_FEATURES

def resample_to_windows(df, window_size='10S'):
    df_time = df.set_index('Timestamp')
    windowed_data = []

    for src_ip, group in df_time.groupby('Src IP'):
        resampled_features = group[CANONICAL_32_FEATURES].resample(window_size).mean().fillna(0.0)
        attack_code = group['Attack_Code'].resample(window_size).max().fillna(0).astype(int)
        tactic_code = group['Tactic_Code'].resample(window_size).max().fillna(0).astype(int)

        resampled_group = pd.concat([resampled_features, attack_code, tactic_code], axis=1)
        resampled_group['Src IP'] = src_ip
        windowed_data.append(resampled_group)

    if not windowed_data:
        return pd.DataFrame(columns=CANONICAL_32_FEATURES + ['Attack_Code', 'Tactic_Code', 'Src IP'])

    return pd.concat(windowed_data).reset_index()

def generate_sliding_windows(windowed_df, T=15):
    X_list, y_state, y_attack, y_tactic = [], [], [], []

    for src_ip, group in windowed_df.groupby('Src IP'):
        group = group.sort_values('Timestamp')
        features = group[CANONICAL_32_FEATURES].values.astype(np.float32)
        attacks = group['Attack_Code'].values
        tactics = group['Tactic_Code'].values

        if len(features) < T + 1:
            pad_len = (T + 1) - len(features)
            pad_feats = np.zeros((pad_len, features.shape[-1]), dtype=np.float32)
            features = np.vstack([pad_feats, features])
            attacks = np.pad(attacks, (pad_len, 0), mode='constant', constant_values=0)
            tactics = np.pad(tactics, (pad_len, 0), mode='constant', constant_values=0)

        for i in range(len(features) - T):
            X_list.append(features[i: i + T])
            y_state.append(features[i + T])
            y_attack.append(attacks[i + T])
            y_tactic.append(tactics[i + T])

    X = np.array(X_list, dtype=np.float32)
    return (
        X,
        np.array(y_state, dtype=np.float32),
        np.array(y_attack, dtype=np.int32),
        np.array(y_tactic, dtype=np.int32)
    )

def build_sequences_pipeline(df, window_size='10S', T=15):
    windowed_df = resample_to_windows(df, window_size=window_size)
    X, y_state, y_attack, y_tactic = generate_sliding_windows(windowed_df, T=T)
    return X, {"state": y_state, "attack": y_attack, "tactic": y_tactic}