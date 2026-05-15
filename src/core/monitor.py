import psutil
import time
import os
import sqlite3
from datetime import datetime

class ServerMonitor:
    def __init__(self, db_path='database/metrics.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS server_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_usage REAL,
                ram_usage REAL,
                disk_usage REAL,
                network_in REAL,
                network_out REAL
            )
        ''')
        conn.close()

    def collect_metrics(self):
        metrics = {
            'cpu_usage': psutil.cpu_percent(interval=1),
            'ram_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_in': psutil.net_io_counters().bytes_recv,
            'network_out': psutil.net_io_counters().bytes_sent
        }
        return metrics

    def persist_metrics(self, metrics):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO server_metrics (cpu_usage, ram_usage, disk_usage, network_in, network_out)
            VALUES (:cpu_usage, :ram_usage, :disk_usage, :network_in, :network_out)
        ''', metrics)
        conn.commit()
        conn.close()

if __name__ == "__main__":
    monitor = ServerMonitor()
    print("Collecting metrics for 5 seconds...")
    for _ in range(5):
        m = monitor.collect_metrics()
        print(f"Metrics: {m}")
        monitor.persist_metrics(m)
        time.sleep(2)
