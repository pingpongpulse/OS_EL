# PhaseSentinel - AI-Powered Program Profiler

A professional-grade Flask web application for runtime profiling, phase detection, deadlock analysis, and AI-powered optimization recommendations.

## 🎯 Features

- **Real-time Metrics Collection**: CPU, memory, disk I/O, network monitoring
- **Phase Segmentation**: Automatic classification into CPU-bound, I/O-bound, memory-bound phases
- **Bottleneck Detection**: Identifies performance bottlenecks with severity levels
- **Deadlock Analysis**: Graph-based cycle detection in lock wait-for graphs
- **Security Anomaly Detection**: ML-powered anomaly detection (optional trained models)
- **Optimization Recommendations**: Phase-specific optimization suggestions with predicted speedup
- **Dark Theme Dashboard**: Professional, responsive UI with Chart.js visualizations
- **RESTful API**: Complete API for integration with external tools

## 🏗️ Architecture

```
PhaseSentinel/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── phaseprofiler.py       # Phase detection and metrics collection
│   ├── deadlock_detector.py   # Deadlock risk analysis
│   ├── anomaly_detector.py    # Security anomaly detection
│   ├── recommender.py         # Optimization recommendations
│   ├── requirements.txt       # Python dependencies
│   ├── models/                # ML models (anomaly_model.pkl, regression_model.pkl)
│   ├── data/                  # Metrics and logs
│   └── tests/                 # Unit tests
├── frontend/
│   ├── templates/
│   │   ├── index.html        # Hero landing page
│   │   ├── dashboard.html    # Real-time metrics dashboard
│   │   └── results.html      # Analysis results and recommendations
│   └── static/
│       ├── css/style.css     # Dark theme styling
│       └── js/charts.js      # Chart.js integration
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip or conda

### Installation

1. **Clone or navigate to the project:**
```bash
cd backend
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Ensure models directory exists:**
```bash
mkdir -p models
```

4. **Run the Flask server:**
```bash
python app.py
```

5. **Open in browser:**
Navigate to `http://localhost:5000`

## 📊 How It Works

### 1. **Profiling** (`/api/profile`)
- Collects system metrics every 0.5 seconds
- Profiles CPU%, memory%, I/O, network usage
- Runs for specified duration (1-300 seconds)

### 2. **Phase Detection** (phaseprofiler.py)
- **CPU-bound**: CPU usage > 70%
- **Memory-bound**: Memory growth > 10MB/s
- **I/O-bound**: I/O wait > 50%
- **Idle**: CPU < 30%, no significant activity

### 3. **Bottleneck Identification**
Rule-based classification identifies:
- High CPU usage phases
- Memory pressure patterns
- I/O bottlenecks
- Severity levels (high/medium/low)

### 4. **Deadlock Detection** (deadlock_detector.py)
- Builds directed wait-for graph
- Detects cycles using networkx
- Returns risk level and recommendations

### 5. **Anomaly Detection** (anomaly_detector.py)
- If `models/anomaly_model.pkl` exists: Uses pre-trained ML model
- Falls back to rule-based detection:
  - CPU > 95%: Possible crypto-mining
  - Memory > 90%: Possible memory leak
  - I/O > 1000 MB: Unusual activity

### 6. **Optimization Recommendations** (recommender.py)
- If `models/regression_model.pkl` exists: Predicts speedup from metrics
- Falls back to phase-specific suggestions:
  - **CPU-bound**: Parallelization, algorithm optimization
  - **I/O-bound**: Asynchronous I/O, caching, connection pooling
  - **Memory-bound**: Data structure optimization, generators
  - **Mixed**: Multi-strategy approach

## 🔌 API Endpoints

### Core Endpoints

```
POST   /api/profile                Start profiling session
GET    /api/results/<result_id>    Get cached results
GET    /api/health                 Health check

# Legacy endpoints (also supported)
POST   /api/classify               Rule-based bottleneck classification
GET/POST /api/deadlock             Deadlock analysis
POST   /api/anomaly                Anomaly detection
POST   /api/recommendations        Get optimization recommendations
```

### Request/Response Format

**POST /api/profile**
```json
Request:
{
  "duration": 10
}

Response:
{
  "id": "uuid-string",
  "timestamp": "ISO-8601",
  "duration": 10,
  "phases": [
    {
      "start": 0,
      "end": 5.2,
      "type": "cpu_bound",
      "duration": 5.2,
      "avg_cpu": 75.3,
      "max_cpu": 89.2
    }
  ],
  "bottlenecks": [
    {
      "type": "CPU",
      "severity": "high",
      "duration": 5.2,
      "message": "High CPU usage (avg 75%)"
    }
  ],
  "anomalies": [],
  "deadlock_risk": false,
  "recommendations": [
    {
      "bottleneck_type": "CPU",
      "phase_type": "cpu_bound",
      "predicted_speedup": 1.5,
      "suggestions": [...]
    }
  ]
}
```

## 🧠 ML Models (Optional)

PhaseSentinel works without models but provides enhanced features with trained models:

### Adding Models

1. **Anomaly Detection Model** (`models/anomaly_model.pkl`)
   - Scikit-learn estimator (IsolationForest, OneClassSVM, etc.)
   - Input features: CPU%, memory%, memory_used_gb, disk_read_mb, disk_write_mb, network_sent_mb, network_recv_mb
   - Predict method returns -1 for anomalies, 1 for normal
   - Optional: decision_function or score_samples methods for anomaly scores

2. **Regression Model** (`models/regression_model.pkl`)
   - Scikit-learn regressor (LinearRegression, RandomForest, etc.)
   - Input features: Same as anomaly model
   - Output: Predicted speedup multiplier (1.0 = no improvement, 1.5 = 50% faster)

### Training Your Own Models

```python
from sklearn.ensemble import IsolationForest, RandomForestRegressor
import joblib

# Anomaly detection model
anomaly_model = IsolationForest(contamination=0.1)
anomaly_model.fit(X_train_metrics)  # Your training data
joblib.dump(anomaly_model, 'models/anomaly_model.pkl')

# Regression model
regression_model = RandomForestRegressor()
regression_model.fit(X_train_metrics, y_speedup)  # Your training data
joblib.dump(regression_model, 'models/regression_model.pkl')
```

## 🎨 Frontend Design

- **Theme**: Dark mode (Deep Navy #0a192f + Electric Blue #64ffda)
- **Framework**: Vanilla JS (no heavy dependencies)
- **Charts**: Chart.js for metrics visualization
- **Responsive**: Desktop-first, mobile-friendly grid layout
- **Animations**: Subtle CSS transitions (0.3s ease)

### Pages

1. **index.html** - Hero landing page with quick-start CTA
2. **dashboard.html** - Real-time metrics charts, phase timeline, bottleneck display
3. **results.html** - Analysis results, anomalies, deadlock info, recommendations

## 📝 Configuration

### Flask Configuration
```python
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
```

### Profiler Configuration
```python
profiler = PhasProfiler(sample_interval=0.5)  # Sample every 0.5 seconds
```

### Phase Thresholds
```python
CPU_THRESHOLD = 70.0      # CPU > 70% = CPU-bound
MEMORY_THRESHOLD = 70.0   # Memory > 70% = Memory-bound
IO_THRESHOLD = 50.0       # I/O wait > 50% = I/O-bound
```

## 🔧 Troubleshooting

### Models Not Loading
```
⚠️ "Model not loaded" warning
```
- Models are optional; the app works without them
- Check that `models/` directory exists
- Ensure models are valid scikit-learn pickles
- Check file permissions

### High Memory Usage During Profiling
- Reduce profiling duration
- Increase `sample_interval` (default 0.5s)
- Use smaller sample sizes

### Slow Dashboard
- Clear browser cache
- Check network latency
- Reduce chart data point density

## 📚 API Examples

### Quick Profile
```bash
curl -X POST http://localhost:5000/api/profile \
  -H "Content-Type: application/json" \
  -d '{"duration": 10}'
```

### Get Health Status
```bash
curl http://localhost:5000/api/health
```

### Fetch Results
```bash
curl http://localhost:5000/api/results/[result-id]
```

## 🧪 Testing

Run unit tests:
```bash
python -m pytest backend/tests/ -v
```

## 📦 Production Deployment

### With Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

### With Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:app"]
```

### Environment Variables
```bash
FLASK_ENV=production
FLASK_DEBUG=false
PYTHONUNBUFFERED=1
```

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📞 Support

For issues, questions, or suggestions:
- Check the [GitHub Issues](https://github.com/pingpongpulse/OS_EL)
- Review existing documentation

---

**Made with ⚡ by PhaseSentinel Team**
