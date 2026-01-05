# PhaseProfiler Web Project

AI-Powered Performance Profiling & Optimization Tool

A web application that profiles system metrics, detects execution phases, classifies bottlenecks using ML, and provides optimization recommendations with predicted speedup improvements.

## 📁 Project Structure

This project is split into **Frontend** and **Backend** for clear separation of concerns:

```
OS_EL/
├── backend/              # Backend (Logic + Data + AI)
│   ├── app.py           # Flask server (routes, API endpoints)
│   ├── phaseprofiler.py # Mono profiler script (collect metrics, detect phases, save CSV)
│   ├── requirements.txt # Dependencies (Flask, psutil, sklearn, matplotlib, etc.)
│   ├── README.md        # Backend setup + usage instructions
│   │
│   ├── data/            # Profiling run datasets
│   │   └── training_data.csv  # Example collected metrics
│   │
│   ├── models/          # Trained ML models
│   │   ├── bottleneck_classifier.pkl   # Random Forest classifier
│   │   └── regression_model.pkl        # Speedup predictor
│   │
│   ├── notebooks/       # Training notebooks
│   │   └── train_model.ipynb  # Train classifier/regression models using CSV data
│   │
│   └── tests/           # Unit tests
│       └── test_profiler.py   # Test metric collection + phase detection
│
└── frontend/            # Frontend (User Interface)
    ├── static/          # Frontend assets
    │   ├── css/
    │   │   └── style.css     # Dashboard styling
    │   ├── js/
    │   │   └── charts.js     # Chart.js scripts for phase timeline
    │   └── images/           # Icons, logos
    │
    └── templates/       # HTML templates (Flask Jinja2)
        ├── index.html        # Homepage (start profiling)
        ├── dashboard.html    # Interactive dashboard (metrics, phases, bottlenecks)
        └── results.html      # Before/after comparison
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Flask Server

```bash
cd backend
python app.py
```

The server will start on `http://localhost:5000`

### 3. Access the Web Interface

Open your browser and navigate to:
- **Homepage**: `http://localhost:5000/`
- **Dashboard**: `http://localhost:5000/dashboard`
- **Results**: `http://localhost:5000/results`

## 🔄 How It Works

1. **User opens website** → Flask (`backend/app.py`) serves `frontend/templates/index.html`
2. **User starts profiling** → Backend runs `backend/phaseprofiler.py`, saves metrics to `backend/data/training_data.csv`
3. **Backend loads ML models** → Classifies bottlenecks, predicts optimization impact
4. **Frontend dashboard** → Displays metrics + phases via Chart.js graphs
5. **Results page** → Shows recommendations and predicted speedup

## 📊 Key Features

- ✅ Real-time system metrics collection (CPU, Memory, I/O, Network)
- ✅ Automatic phase detection (CPU-bound, I/O-bound, Memory-bound, Mixed, Idle)
- ✅ AI-powered bottleneck classification using Random Forest
- ✅ Optimization impact prediction using regression models
- ✅ Interactive dashboards with Chart.js visualizations
- ✅ Actionable optimization recommendations

## 🧪 Training Models

1. Collect training data using the profiler
2. Open `backend/notebooks/train_model.ipynb` in Jupyter
3. Run all cells to train classifier and regression models
4. Trained models will be saved to `backend/models/` directory

## 📝 Responsibilities

### Backend (`backend/`)
- **Collect metrics** (CPU, I/O, memory) → `phaseprofiler.py`
- **Detect phases** → `phaseprofiler.py`
- **Train models** → `notebooks/train_model.ipynb`
- **Store datasets** → `data/`
- **Serve results via Flask API** → `app.py`
- **Load models** → `models/`

### Frontend (`frontend/`)
- **Homepage (`index.html`)** → Start profiling, upload program
- **Dashboard (`dashboard.html`)** → Show real-time metrics, phase timeline, bottleneck classification
- **Results (`results.html`)** → Show recommendations + predicted impact
- **Styling (`style.css`)** → Clean, modern UI
- **Charts (`charts.js`)** → Interactive phase timeline + bottleneck visualization

## 🧪 Testing

Run unit tests:
```bash
cd backend
python -m pytest tests/
```

Or run individual test file:
```bash
python tests/test_profiler.py
```

## 📚 Documentation

- Backend documentation: `backend/README.md`
- API endpoints: See `backend/app.py` for Flask routes
- Profiler usage: See `backend/phaseprofiler.py` for command-line options

## 🔧 Configuration

- Default profiling duration: 60 seconds
- Default sampling interval: 1 second
- Max upload file size: 16MB
- Models location: `backend/models/`
- Data location: `backend/data/`

## 📄 License

This project is part of an OS/EL course assignment.

---

**Note**: This split makes it clear:
- **Backend = brains (profiling, AI, data)**
- **Frontend = face (dashboard, charts, user interaction)**

