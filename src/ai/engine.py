import joblib
import numpy as np
import os
import time

class AIInferenceEngine:
    """
    Expert-level AI Engine for server health diagnostics.
    Uses multi-factor correlation for outage prediction.
    """
    def __init__(self, forecast_model_path, anomaly_model_path=None):
        self.forecast_model = joblib.load(forecast_model_path) if os.path.exists(forecast_model_path) else None
        self.anomaly_model = joblib.load(anomaly_model_path) if anomaly_model_path and os.path.exists(anomaly_model_path) else None

    def predict_next(self, recent_metrics):
        if not self.forecast_model or len(recent_metrics) < 5:
            return None
        input_data = np.array(recent_metrics).reshape(1, -1)
        return self.forecast_model.predict(input_data)[0]

    def detect_anomaly(self, current_metrics_vec):
        if not self.anomaly_model:
            return 1
        # Handle cases where model might expect different feature counts
        vec = np.array(current_metrics_vec).reshape(1, -1)
        try:
            return self.anomaly_model.predict(vec)[0]
        except Exception:
            # Fallback if vec size mismatch during model upgrades
            return 1

    def get_intelligent_alert(self, current_metrics, predicted_cpu, is_anomaly):
        """
        Expert diagnostic engine: Correlates forecast trends, load, and I/O pressure.
        """
        points = 0.0
        reasons = []

        # 1. Forecast Pressure
        if predicted_cpu and predicted_cpu > 80:
            points += 35
            reasons.append(f"Forecast trend predicts CPU surge to {predicted_cpu:.1f}%")
        
        # 2. Behavioral Drift
        if is_anomaly:
            points += 25
            reasons.append("Behavioral drift detected (statistical outlier)")

        # 3. Resource Exhaustion
        if current_metrics.get('ram_usage', 0) > 90:
            points += 20
            reasons.append("Critical memory saturation")
        
        # 4. Expert Load Factors (I/O & Load Avg)
        load1 = current_metrics.get('load_avg_1', 0)
        if load1 > 5.0:
            points += 15
            reasons.append(f"Load average is abnormally high ({load1:.1f})")

        disk_io = current_metrics.get('disk_write_rate', 0) + current_metrics.get('disk_read_rate', 0)
        if disk_io > 50 * 1024 * 1024: # 50 MB/s
            points += 10
            reasons.append("High Disk I/O throughput detected")

        # Severity Scaling
        prob_failure = min(points, 99.0)
        severity = "STABLE"
        if prob_failure > 75: severity = "CRITICAL (P0)"
        elif prob_failure > 40: severity = "WARNING (P1)"
        elif prob_failure > 15: severity = "ELEVATED"

        if not reasons: reasons = ["System behavior is nominal"]

        return {
            "failure_probability": f"{prob_failure}%",
            "severity": severity,
            "is_anomaly": is_anomaly,
            "reasons": reasons
        }
