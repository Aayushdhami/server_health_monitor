from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.responses import HTMLResponse
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
import sys
import logging

logger = logging.getLogger(__name__)

# Basic API Key security setup
API_KEY = os.getenv("API_KEY", "dev-secret-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="Could not validate API KEY")

# Ensure parent directory is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.monitor import ServerMonitor
from src.ai.engine import AIInferenceEngine
from src.ai.assistant import DevOpsAssistant

app = FastAPI(title="AI Server Health Monitor API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify explicit domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    logger.warning(f"AI Engine could not be fully initialized: {e}")
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
def get_health(api_key: str = Depends(get_api_key)):
    """Returns current system health metrics and AI predictions."""
    metrics = monitor.collect_metrics()
    
    # Run AI Prediction if engine is available
    prediction = None
    alert = None
    if engine:
        # Get last 5 metrics for prediction
        try:
            with sqlite3.connect(monitor.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT cpu_usage FROM server_metrics ORDER BY id DESC LIMIT 5")
                rows = cursor.fetchall()
                recent = [row[0] for row in rows][::-1]
        except sqlite3.Error as e:
            logger.error(f"Database error reading history: {e}")
            recent = []
        
        if len(recent) >= 5:
            prediction = engine.predict_next(recent)
            # Detect anomaly based on current vector
            current_vec = [
                metrics['cpu_usage'], 
                metrics['ram_usage'], 
                metrics['network_in'],
                metrics['disk_read_rate'],
                metrics['disk_write_rate']
            ]
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
def get_history(limit: int = 20, api_key: str = Depends(get_api_key)):
    """Returns historical metrics from the database."""
    try:
        with sqlite3.connect(monitor.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM server_metrics ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return []

@app.post("/assistant/query")
def ask_assistant(request: QueryRequest, api_key: str = Depends(get_api_key)):
    """Queries the RAG DevOps Assistant."""
    results = assistant.query(request.text)
    return {"query": request.text, "results": results}

@app.get("/api")
def read_api_root():
    return {"message": "Server Health Monitor API is running. Visit /docs for documentation."}
