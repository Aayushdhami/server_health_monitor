import threading
import time
import uvicorn
import os
import sys
import logging

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.core.monitor import ServerMonitor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def background_monitoring():
    """Background task to collect and persist metrics every 10 seconds."""
    logger.info("🚀 Background monitoring started...")
    monitor = ServerMonitor()
    while True:
        try:
            metrics = monitor.collect_metrics()
            monitor.persist_metrics(metrics)
            # logger.debug(f"Collected metrics: {metrics}")
        except Exception as e:
            logger.error(f"Error in monitoring task: {e}")
        time.sleep(10)

if __name__ == "__main__":
    logger.info("--- AI Server Health Monitor ---")
    
    # 1. Start background monitoring thread
    monitor_thread = threading.Thread(target=background_monitoring, daemon=True)
    monitor_thread.start()
    
    # 2. Check for models
    if not os.path.exists('models/cpu_model.joblib'):
        logger.warning("⚠️ Warning: AI models not found. Run 'python scripts/train_model.py' to enable AI features.")
    
    # 3. Start FastAPI server
    logger.info("🌐 Starting API server on http://localhost:8000")
    uvicorn.run("src.web.app:app", host="0.0.0.0", port=8000, reload=False)
