import threading
import time
import uvicorn
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.core.monitor import ServerMonitor

def background_monitoring():
    """Background task to collect and persist metrics every 10 seconds."""
    print("🚀 Background monitoring started...")
    monitor = ServerMonitor()
    while True:
        try:
            metrics = monitor.collect_metrics()
            monitor.persist_metrics(metrics)
            # print(f"Collected metrics: {metrics}")
        except Exception as e:
            print(f"Error in monitoring task: {e}")
        time.sleep(10)

if __name__ == "__main__":
    print("--- AI Server Health Monitor ---")
    
    # 1. Start background monitoring thread
    monitor_thread = threading.Thread(target=background_monitoring, daemon=True)
    monitor_thread.start()
    
    # 2. Check for models
    if not os.path.exists('models/cpu_model.joblib'):
        print("⚠️ Warning: AI models not found. Run 'python scripts/train_model.py' to enable AI features.")
    
    # 3. Start FastAPI server
    print("🌐 Starting API server on http://localhost:8000")
    uvicorn.run("src.web.app:app", host="0.0.0.0", port=8000, reload=False)
