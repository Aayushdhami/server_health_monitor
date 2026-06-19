import psutil
import time
import os
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ServerMonitor:
    def __init__(self, db_path='database/metrics.db'):
        self.db_path = os.path.abspath(db_path)
        
        # Internal state for rate calculation (Network & Disk I/O)
        net_counters = psutil.net_io_counters()
        disk_counters = psutil.disk_io_counters()
        
        self._last_net_in = net_counters.bytes_recv
        self._last_net_out = net_counters.bytes_sent
        self._last_disk_read = disk_counters.read_bytes
        self._last_disk_write = disk_counters.write_bytes
        self._last_time = time.time()
        
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('PRAGMA journal_mode=WAL;')
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS server_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        cpu_usage REAL,
                        ram_usage REAL,
                        disk_usage REAL,
                        network_in REAL,
                        network_out REAL,
                        disk_read_rate REAL,
                        disk_write_rate REAL,
                        load_avg_1 REAL,
                        load_avg_5 REAL,
                        cpu_cores_json TEXT
                    )
                ''')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON server_metrics(timestamp);')
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")

    def collect_metrics(self):
        """Advanced metrics collection including I/O rates and per-core usage."""
        current_time = time.time()
        net_counters = psutil.net_io_counters()
        disk_counters = psutil.disk_io_counters()
        
        time_delta = current_time - self._last_time
        if time_delta <= 0: time_delta = 1.0 # Prevent div by zero

        # Network Rates
        net_in_rate = (net_counters.bytes_recv - self._last_net_in) / time_delta
        net_out_rate = (net_counters.bytes_sent - self._last_net_out) / time_delta
        
        # Disk I/O Rates
        disk_read_rate = (disk_counters.read_bytes - self._last_disk_read) / time_delta
        disk_write_rate = (disk_counters.write_bytes - self._last_disk_write) / time_delta

        # Update last states
        self._last_net_in = net_counters.bytes_recv
        self._last_net_out = net_counters.bytes_sent
        self._last_disk_read = disk_counters.read_bytes
        self._last_disk_write = disk_counters.write_bytes
        self._last_time = current_time

        # Advanced System Load (Linux/Unix has these native, Windows needs emulation)
        try:
            load1, load5, _ = psutil.getloadavg()
        except (AttributeError, OSError):
            load1, load5 = 0.0, 0.0 # Windows fallback

        per_core_cpu = psutil.cpu_percent(percpu=True)

        metrics = {
            'cpu_usage': psutil.cpu_percent(),
            'ram_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage(os.path.abspath(os.sep)).percent,
            'network_in': net_in_rate,
            'network_out': net_out_rate,
            'disk_read_rate': disk_read_rate,
            'disk_write_rate': disk_write_rate,
            'load_avg_1': load1,
            'load_avg_5': load5,
            'cpu_cores': per_core_cpu
        }
        return metrics

    def persist_metrics(self, metrics):
        import json
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO server_metrics (
                        cpu_usage, ram_usage, disk_usage, network_in, network_out,
                        disk_read_rate, disk_write_rate, load_avg_1, load_avg_5, cpu_cores_json
                    )
                    VALUES (
                        :cpu_usage, :ram_usage, :disk_usage, :network_in, :network_out,
                        :disk_read_rate, :disk_write_rate, :load_avg_1, :load_avg_5, :cpu_cores_json
                    )
                ''', {**metrics, 'cpu_cores_json': json.dumps(metrics['cpu_cores'])})
        except sqlite3.Error as e:
            logger.error(f"Failed to persist metrics: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    monitor = ServerMonitor()
    logger.info("Expert Metrics Collection...")
    for _ in range(3):
        m = monitor.collect_metrics()
        logger.info(f"Metrics (Summary): CPU {m['cpu_usage']}% | Disk Read {m['disk_read_rate']/1024:.1f} KB/s")
        monitor.persist_metrics(m)
        time.sleep(2)
