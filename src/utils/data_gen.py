import numpy as np
import pandas as pd

def create_timeseries_features(data, window_size=5):
    """
    Converts a flat list of metrics into a windowed dataset for ML.
    """
    X, y = [], []
    for i in range(len(data) - window_size):
        X.append(data[i:i + window_size])
        y.append(data[i + window_size])
    return np.array(X), np.array(y)

def generate_synthetic_data(samples=200):
    """
    Generates synthetic CPU data with a daily pattern and random noise.
    """
    time_indices = np.arange(samples)
    # Base usage + Sine wave for daily pattern + Random noise + Occasional spikes
    base = 20
    pattern = 15 * np.sin(time_indices / 10)
    noise = np.random.normal(0, 5, samples)
    spikes = np.where(np.random.rand(samples) > 0.95, 40, 0)

    cpu_usage = np.clip(base + pattern + noise + spikes, 0, 100)
    return pd.DataFrame({'cpu_usage': cpu_usage})

if __name__ == "__main__":
    df = generate_synthetic_data()
    print(df.head())
    X, y = create_timeseries_features(df['cpu_usage'].values)
    print(f"Features shape: {X.shape}, Target shape: {y.shape}")
