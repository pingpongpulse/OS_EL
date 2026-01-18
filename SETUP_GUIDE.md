# PhaseSentinel - Setup & Deployment Guide

## ✅ Pre-Launch Checklist

- [x] Backend Flask app (`app.py`)
- [x] Phase profiler module (`phaseprofiler.py`)
- [x] Deadlock detector (`deadlock_detector.py`)
- [x] Anomaly detector (`anomaly_detector.py`)
- [x] Recommender engine (`recommender.py`)
- [x] Frontend HTML (index, dashboard, results)
- [x] Dark theme CSS
- [x] Chart.js integration (charts.js)
- [x] Requirements.txt with all dependencies
- [x] README documentation
- [x] Startup scripts (start.sh, start.bat)

## 🚀 Quick Start (3 Minutes)

### Windows Users
```bash
# 1. Navigate to project root
cd c:\PROJECTS\OS_EL

# 2. Run the startup script
start.bat

# 3. Open browser to http://localhost:5000
```

### macOS / Linux Users
```bash
# 1. Navigate to project root
cd /path/to/OS_EL

# 2. Make script executable
chmod +x start.sh

# 3. Run the startup script
./start.sh

# 4. Open browser to http://localhost:5000
```

## 📋 Manual Installation

If startup scripts don't work:

```bash
# 1. Navigate to backend
cd backend

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Create data and models directories
mkdir -p data models

# 4. Start the Flask server
python app.py

# 5. Access in browser
# Frontend: http://localhost:5000
# API: http://localhost:5000/api/health
```

## 🔍 Verification Steps

### 1. Check Installation
```bash
python verify_build.py
```

Expected output:
```
✓ Backend Python files present
✓ Frontend HTML templates present
✓ Static assets present
✓ All directories created
```

### 2. Test API Health
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-18T...",
  "models_loaded": {
    "anomaly": false,
    "regression": false
  },
  "warnings": [
    "Anomaly detection model pending training",
    "Speedup prediction model pending training"
  ]
}
```

### 3. Test Profile Endpoint
```bash
curl -X POST http://localhost:5000/api/profile \
  -H "Content-Type: application/json" \
  -d '{"duration": 5}'
```

Expected response:
```json
{
  "id": "uuid-string",
  "status": "success",
  "duration": 5,
  "phases": [...],
  "bottlenecks": [...],
  "recommendations": [...]
}
```

## 🎨 Frontend Access

| URL | Purpose |
|-----|---------|
| `http://localhost:5000/` | Hero landing page with quick-start |
| `http://localhost:5000/dashboard` | Real-time metrics dashboard |
| `http://localhost:5000/results/<id>` | Analysis results page |

## 🔑 Key Files & Locations

```
backend/
├── app.py                 # Main Flask application
├── phaseprofiler.py       # Metrics collection & phase detection
├── deadlock_detector.py   # Deadlock risk analysis
├── anomaly_detector.py    # Security anomaly detection
├── recommender.py         # Optimization recommendations
├── requirements.txt       # Python dependencies
├── models/                # ML models storage (optional)
│   ├── anomaly_model.pkl      (optional)
│   └── regression_model.pkl   (optional)
└── data/                  # Runtime data storage
    ├── lock_logs.json
    ├── training_data.csv
    └── optimization_results.csv

frontend/
├── templates/
│   ├── index.html         # Hero/landing page
│   ├── dashboard.html     # Metrics dashboard
│   └── results.html       # Results page
└── static/
    ├── css/style.css      # Dark theme styling
    └── js/charts.js       # Chart.js integration
```

## ⚙️ Configuration

### Flask Configuration (app.py)
```python
UPLOAD_FOLDER = './data'              # Data storage
MODELS_FOLDER = './models'            # ML models storage
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
FLASK_ENV = 'development'             # Change to 'production' for deploy
FLASK_DEBUG = True                    # Change to False for production
```

### Profiler Settings (phaseprofiler.py)
```python
sample_interval = 0.5                 # Sample every 0.5 seconds
duration = 10                         # Default profiling duration
```

### Phase Detection Thresholds
```python
CPU_THRESHOLD = 70.0      # CPU > 70% → cpu_bound
MEMORY_THRESHOLD = 70.0   # Memory > 70% → memory_bound
IO_THRESHOLD = 50.0       # I/O > 50% → io_bound
IDLE_CPU_THRESHOLD = 30.0
```

## 📊 Data Flow

```
1. User clicks "Start Profiling"
   ↓
2. Frontend POST to /api/profile with duration
   ↓
3. Backend starts PhasProfiler.profile()
   ↓
4. Collect metrics every 0.5s for specified duration
   ↓
5. Segment metrics into phases (CPU/IO/Memory-bound)
   ↓
6. Run DeadlockDetector.detect()
   ↓
7. Run AnomalyDetector.detect()
   ↓
8. Get recommendations from Recommender.recommend()
   ↓
9. Return JSON with id, phases, bottlenecks, anomalies, recommendations
   ↓
10. Frontend redirects to /results/<id>
   ↓
11. Display charts, bottlenecks, anomalies, recommendations
```

## 🧠 Adding ML Models

### Without Models (Default)
- Phase detection: Rule-based (CPU%, memory%, I/O%)
- Anomaly detection: Rule-based (thresholds)
- Recommendations: Generic suggestions

### With Trained Models
- Place models in `backend/models/`
- Anomaly model: `anomaly_model.pkl` (scikit-learn estimator)
- Regression model: `regression_model.pkl` (scikit-learn regressor)

### Training Example
```python
from sklearn.ensemble import IsolationForest, RandomForestRegressor
import joblib
import pandas as pd

# Load your training data
train_df = pd.read_csv('training_data.csv')
X = train_df[['cpu_percent', 'memory_percent', 'memory_used_gb', 
               'disk_read_mb', 'disk_write_mb', 'network_sent_mb', 'network_recv_mb']]
y_anomaly = train_df['is_anomaly']  # Binary labels
y_speedup = train_df['speedup']     # Numeric speedup values

# Train anomaly model
anomaly_model = IsolationForest(contamination=0.1)
anomaly_model.fit(X)
joblib.dump(anomaly_model, 'backend/models/anomaly_model.pkl')

# Train regression model
regression_model = RandomForestRegressor()
regression_model.fit(X, y_speedup)
joblib.dump(regression_model, 'backend/models/regression_model.pkl')
```

## 🚨 Troubleshooting

### Issue: "Port 5000 already in use"
```bash
# Windows: Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux: Kill process on port 5000
lsof -i :5000
kill -9 <PID>
```

### Issue: "ModuleNotFoundError"
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Issue: "Templates not found"
```bash
# Verify folder structure
ls -la frontend/templates/
ls -la frontend/static/css/
ls -la frontend/static/js/
```

### Issue: Models show as "pending training"
This is normal! Models are optional. The app works fine without them.
To use models, train them and place in `backend/models/`

## 📈 Performance Tips

### For Large Datasets
- Reduce profiling duration (use 5-10 seconds)
- Increase `sample_interval` to 1.0s
- Process in batches

### For High CPU Usage
- Use threading instead of multiprocessing
- Reduce chart refresh rate
- Limit metrics retention

### For Memory Optimization
- Clear data directory periodically
- Use database instead of CSV
- Implement data compression

## 🔒 Security Considerations

### For Production
1. Set `FLASK_ENV=production`
2. Set `FLASK_DEBUG=False`
3. Use HTTPS/SSL certificates
4. Implement authentication/authorization
5. Validate all user inputs
6. Use environment variables for secrets
7. Rate limit API endpoints
8. Run with Gunicorn (not Flask dev server)

### Example Production Setup
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
```

## 📚 API Documentation

### Available Endpoints

```
GET    /                          Serve index.html
GET    /dashboard                 Serve dashboard.html
GET    /results/<result_id>       Serve results.html

POST   /api/profile               Start profiling session
GET    /api/results/<result_id>   Get cached results
GET    /api/health                Health check

# Legacy endpoints (still supported)
GET    /api/metrics               Get metrics data
GET    /api/phases                Get phase classification
POST   /api/classify              Rule-based classification
GET/POST /api/deadlock            Deadlock analysis
POST   /api/anomaly               Anomaly detection
POST   /api/recommendations       Get recommendations
POST   /api/predict-speedup       Predict optimization speedup
POST   /api/collect-data          Collect user data for training
POST   /api/merge-all-data        Merge user data files
GET    /api/user-data-stats       User data statistics
```

## 🎯 Development Roadmap

- [x] Phase profiling and detection
- [x] Deadlock detection
- [x] Anomaly detection
- [x] Optimization recommendations
- [x] Flask API
- [x] Web dashboard
- [ ] WebSocket for real-time updates
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] User authentication
- [ ] Data export (CSV, PDF)
- [ ] Advanced anomaly detection models
- [ ] Predictive recommendations
- [ ] Comparison between runs
- [ ] Historical analysis

## 📞 Support & Feedback

For issues, questions, or feature requests:
1. Check the README.md
2. Review the code comments
3. Check GitHub Issues
4. Create a new issue with details

---

**PhaseSentinel © 2024 - Ready to profile! ⚡**
