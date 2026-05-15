import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from src.utils.data_gen import generate_synthetic_data, create_timeseries_features

def train_forecasting_model():
    print("Training CPU Forecasting Model...")
    df = generate_synthetic_data(samples=500)
    X, y = create_timeseries_features(df['cpu_usage'].values, window_size=5)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    model_path = 'models/cpu_model.joblib'
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, model_path)
    print(f"✅ Forecasting model saved to {model_path}")

def train_anomaly_model():
    print("Training Anomaly Detection Model...")
    # Normal behavior: [CPU, RAM, Network]
    normal_behavior = np.random.normal(loc=[30, 40, 1000], scale=[5, 5, 200], size=(200, 3))
    
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(normal_behavior)
    
    model_path = 'models/anomaly_model.joblib'
    joblib.dump(model, model_path)
    print(f"✅ Anomaly model saved to {model_path}")

if __name__ == "__main__":
    train_forecasting_model()
    train_anomaly_model()
