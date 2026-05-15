import joblib
import numpy as np
import os
import time

class AIInferenceEngine:
    """
    Core AI Engine for predicting server metrics and detecting anomalies.
    """
    def __init__(self, forecast_model_path, anomaly_model_path=None):
        self.forecast_model = joblib.load(forecast_model_path) if os.path.exists(forecast_model_path) else None
        self.anomaly_model = joblib.load(anomaly_model_path) if anomaly_model_path and os.path.exists(anomaly_model_path) else None

    def predict_next(self, recent_metrics):
        """
        Predicts the next metric value based on a window of recent readings.
        """
        if not self.forecast_model or len(recent_metrics) < 5:
            return None
        input_data = np.array(recent_metrics).reshape(1, -1)
        return self.forecast_model.predict(input_data)[0]

    def detect_anomaly(self, current_metrics_vec):
        """
        Detects if current metrics represent an anomaly.
        Returns -1 for outliers and 1 for normal data.
        """
        if not self.anomaly_model:
            return 1
        pred = self.anomaly_model.predict(np.array(current_metrics_vec).reshape(1, -1))
        return pred[0]

    def get_intelligent_alert(self, current_metrics, predicted_cpu, is_anomaly):
        """
        Correlates multiple signals to estimate failure probability and severity.
        """
        prob_failure = 0.0

        # Correlation Logic
        if predicted_cpu and predicted_cpu > 85: 
            prob_failure += 40
        if is_anomaly: 
            prob_failure += 30
        if current_metrics.get('ram_usage', 0) > 80: 
            prob_failure += 20

        # Cap probability at 99%
        prob_failure = min(prob_failure, 99.0)

        # Estimated Time to Outage (Heuristic based on trend)
        eto = 60 # Default 60 mins
        if prob_failure > 70: 
            eto = 15
        elif prob_failure > 40: 
            eto = 35

        severity = "LOW"
        if prob_failure > 75: 
            severity = "P0 (CRITICAL)"
        elif prob_failure > 40: 
            severity = "P1 (WARNING)"

        return {
            "failure_probability": f"{prob_failure}%",
            "estimated_outage_mins": eto,
            "severity": severity,
            "is_anomaly": is_anomaly
        }

    def get_risk_assessment(self, pred_cpu, pred_disk=20.0, is_anomaly=False):
        """
        Legacy risk assessment logic.
        """
        score = (pred_cpu * 0.7) + (pred_disk * 0.3)
        if is_anomaly: 
            score += 20

        if score > 80: return 'CRITICAL'
        if score > 60: return 'WARNING'
        return 'HEALTHY'
