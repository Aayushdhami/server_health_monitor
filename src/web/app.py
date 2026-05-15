from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
import sys

# Ensure parent directory is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.monitor import ServerMonitor
from src.ai.engine import AIInferenceEngine
from src.ai.assistant import DevOpsAssistant

app = FastAPI(title="AI Server Health Monitor API")

# Initialize components
monitor = ServerMonitor()
assistant = DevOpsAssistant()

# Paths for models
MODEL_PATH = 'models/cpu_model.joblib'
ANOMALY_PATH = 'models/anomaly_model.joblib'

# Load AI Engine
try:
    engine = AIInferenceEngine(MODEL_PATH, ANOMALY_PATH)
except Exception as e:
    print(f"Warning: AI Engine could not be fully initialized: {e}")
    engine = None

class QueryRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
def read_root():
    template_path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Dashboard template not found. Ensure src/web/templates/index.html exists."

@app.get("/health")
def get_health():
    """Returns current system health metrics and AI predictions."""
    metrics = monitor.collect_metrics()
    
    # Run AI Prediction if engine is available
    prediction = None
    alert = None
    if engine:
        # Get last 5 metrics for prediction
        conn = sqlite3.connect(monitor.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT cpu_usage FROM server_metrics ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        recent = [row[0] for row in rows][::-1]
        conn.close()
        
        if len(recent) >= 5:
            prediction = engine.predict_next(recent)
            # Detect anomaly based on current vector
            current_vec = [metrics['cpu_usage'], metrics['ram_usage'], metrics['network_in']]
            is_anomaly = engine.detect_anomaly(current_vec) == -1
            alert = engine.get_intelligent_alert(metrics, prediction, is_anomaly)
    
    return {
        "current_metrics": metrics,
        "ai_prediction": {
            "next_cpu": round(float(prediction), 2) if prediction else None,
            "status": alert
        }
    }

@app.get("/history")
def get_history(limit: int = 20):
    """Returns historical metrics from the database."""
    conn = sqlite3.connect(monitor.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM server_metrics ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/assistant/query")
def ask_assistant(request: QueryRequest):
    """Queries the RAG DevOps Assistant."""
    results = assistant.query(request.text)
    return {"query": request.text, "results": results}

@app.get("/api")
def read_api_root():
    return {"message": "Server Health Monitor API is running. Visit /docs for documentation."}
