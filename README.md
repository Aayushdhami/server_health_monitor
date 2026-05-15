# AI-Powered Server Health Monitor

A production-grade server health monitoring system that leverages Machine Learning for forecasting, anomaly detection, and a RAG-based DevOps assistant for historical incident analysis.

## 🚀 Features
- **Real-time Monitoring**: Collects system metrics (CPU, RAM, Disk, Network).
- **AI Forecasting**: Predicts future resource usage using Time-Series models.
- **Anomaly Detection**: Identifies unusual patterns in server behavior.
- **DevOps Assistant**: A RAG (Retrieval-Augmented Generation) assistant to query historical incident context.
- **Intelligent Alerting**: Risk-scored alerts based on current and predicted states.

## 📁 Project Structure
```text
server-health-monitor/
├── .github/                # GitHub Actions for CI/CD
├── data/                   # Dataset storage (Raw & Processed)
├── database/               # Local database for metrics (SQLite)
├── models/                 # Pre-trained ML models (.joblib, .pth)
├── notebooks/              # Research and Development notebooks
├── scripts/                # Training and deployment scripts
├── src/                    # Source code
│   ├── ai/                 # AI Engines (Forecasting, RAG Assistant)
│   ├── core/               # Metric collection and Alerting logic
│   ├── utils/              # Helper functions and data generation
│   └── web/                # Dashboard API (FastAPI/Flask)
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

## 🛠️ Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Aayushdhami/server_health_monitor
   cd server-health-monitor
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 📈 Usage
- **Training**: Run `python scripts/train_model.py` to train the AI forecasting models.
- **Monitoring**: Run `python src/main.py` to start the health monitor.

## 📄 License
MIT License
