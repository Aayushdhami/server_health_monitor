import os
import sys
import joblib
import logging
import numpy as np
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils.data_gen import generate_synthetic_data, create_timeseries_features

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def train_forecasting_model():
    logger.info("Training CPU Forecasting Model...")
    # Increase samples for a better dataset
    df = generate_synthetic_data(samples=2000)
    X, y = create_timeseries_features(df['cpu_usage'].values, window_size=5)
    
    # Train/Test split for actual model evaluation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    logger.info(f"Forecasting Model Evaluation -> MAE: {mae:.2f}, RMSE: {rmse:.2f}, R2: {r2:.2f}")
    
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../models'))
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, 'cpu_model.joblib')
    
    joblib.dump(model, model_path)
    logger.info(f"✅ Forecasting model saved to {model_path}")

def train_anomaly_model():
    logger.info("Training Expert Anomaly Detection Model (5 features)...")
    
    # Normal behavior [CPU, RAM, Net, DiskR, DiskW]
    normal_behavior = np.random.normal(
        loc=[30, 40, 1000, 5000, 5000], 
        scale=[5, 5, 200, 1000, 1000], 
        size=(1000, 5)
    )
    
    # Explicit anomalies (high spikes in everything)
    anomalies = np.random.normal(
        loc=[95, 90, 50000, 1000000, 1000000], 
        scale=[2, 2, 5000, 100000, 100000], 
        size=(50, 5)
    )
    
    model = IsolationForest(contamination=0.01, random_state=42)
    model.fit(normal_behavior)
    
    # Evaluation
    normal_preds = model.predict(normal_behavior)
    anomaly_preds = model.predict(anomalies)
    
    fp = np.sum(normal_preds == -1) / len(normal_preds)
    fn = np.sum(anomaly_preds == 1) / len(anomaly_preds)
    
    logger.info(f"Expert Anomaly Evaluation -> FPR: {fp*100:.1f}%, FNR: {fn*100:.1f}%")
    
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../models'))
    model_path = os.path.join(models_dir, 'anomaly_model.joblib')
    
    joblib.dump(model, model_path)
    logger.info(f"✅ Expert Anomaly model saved to {model_path}")

if __name__ == "__main__":
    train_forecasting_model()
    train_anomaly_model()
