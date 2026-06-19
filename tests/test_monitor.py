import os
import sys
import unittest
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.monitor import ServerMonitor

class TestServerMonitor(unittest.TestCase):
    def setUp(self):
        # Use an absolute test path to ensure no relative path issues during tests
        self.test_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_metrics.db'))
        self.monitor = ServerMonitor(db_path=self.test_db_path)

    def tearDown(self):
        if os.path.exists(self.test_db_path):
            # Try removing files safely
            try:
                os.remove(self.test_db_path)
                # Remove WAL/SHM files too if they exist
                if os.path.exists(self.test_db_path + '-wal'):
                    os.remove(self.test_db_path + '-wal')
                if os.path.exists(self.test_db_path + '-shm'):
                    os.remove(self.test_db_path + '-shm')
            except OSError:
                pass
            
    def test_collect_metrics(self):
        metrics = self.monitor.collect_metrics()
        self.assertIn('cpu_usage', metrics)
        self.assertIn('ram_usage', metrics)
        self.assertIn('disk_usage', metrics)
        self.assertIn('network_in', metrics)
        self.assertIn('network_out', metrics)
        
        # Valid percentage bound checks
        self.assertTrue(0 <= metrics['cpu_usage'] <= 100)
        self.assertTrue(0 <= metrics['ram_usage'] <= 100)
        self.assertTrue(0 <= metrics['disk_usage'] <= 100)

    def test_persist_metrics(self):
        metrics = {
            'cpu_usage': 45.0,
            'ram_usage': 60.5,
            'disk_usage': 30.0,
            'network_in': 1024.0,
            'network_out': 2048.0
        }
        self.monitor.persist_metrics(metrics)
        
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT cpu_usage, disk_usage FROM server_metrics ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], 45.0)
            self.assertEqual(row[1], 30.0)

if __name__ == '__main__':
    unittest.main()
