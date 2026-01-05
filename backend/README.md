# PhaseProfiler Backend

Backend logic for PhaseProfiler web application. Handles profiling, AI classification, recommendations, and serving data to the frontend.

## 📁 Structure

```
backend/
├── app.py                  # Flask server (routes, API endpoints)
├── phaseprofiler.py        # Mono profiler script (collect metrics, detect phases, save CSV)
├── requirements.txt        # Dependencies
├── README.md               # This file
├── data/                   # Profiling run datasets
│   └── training_data.csv  # Example collected metrics
├── models/                 # Trained ML models
│   ├── bottleneck_classifier.pkl   # Random Forest classifier
│   └── regression_model.pkl        # Speedup predictor
├── notebooks/              # Training notebooks
│   └── train_model.ipynb  # Train classifier/regression models using CSV data
└── tests/                  # Unit tests
    └── test_profiler.py   # Test metric collection + phase detection
```

## 🚀 Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask server:**
   ```bash
   python app.py
   ```

   The server will start on `http://localhost:5000`

## 📊 Usage

### Running the Profiler

**Option 1: Via Flask API**
- Start the Flask server: `python app.py`
- Use the web interface at `http://localhost:5000`
- Or call the API endpoints directly (see API Documentation below)

**Option 2: Command-line**
```bash
# Profile system-wide metrics for 60 seconds
python phaseprofiler.py --duration 60 --output data/training_data.csv

# Profile a specific program
python phaseprofiler.py /path/to/program.py --duration 120
```

### Training Models

1. Collect training data using the profiler
2. Open `notebooks/train_model.ipynb` in Jupyter
3. Follow the notebook to train classifier and regression models
4. Save trained models to `models/` directory

## 🔌 API Endpoints

### `GET /`
Homepage - start profiling interface

### `GET /dashboard`
Interactive dashboard showing metrics, phases, and bottlenecks

### `GET /results`
Results page showing recommendations and predicted impact

### `POST /api/profile`
Start profiling a program
- Request body: `{"program_path": "...", "duration": 60}`
- Returns: `{"status": "success", "output_file": "training_data.csv"}`

### `GET /api/metrics`
Get collected metrics data
- Returns: `{"status": "success", "metrics": [...], "count": N}`

### `POST /api/classify`
Classify bottlenecks using trained ML model
- Request body: `{"features": [[...], [...]]}`
- Returns: `{"status": "success", "predictions": [...], "probabilities": [...]}`

### `POST /api/predict-speedup`
Predict optimization speedup using regression model
- Request body: `{"features": [[...], [...]]}`
- Returns: `{"status": "success", "speedup": [...], "predicted_improvement": "..."}`

### `GET /api/health`
Health check endpoint
- Returns: `{"status": "healthy", "timestamp": "...", "models_available": {...}}`

## 🧪 Testing

Run unit tests:
```bash
python -m pytest tests/
```

Or run individual test file:
```bash
python tests/test_profiler.py
```

## 📝 Responsibilities

- **Collect metrics** (CPU, I/O, memory) → `phaseprofiler.py`
- **Detect phases** → `phaseprofiler.py`
- **Train models** → `notebooks/train_model.ipynb`
- **Store datasets** → `data/`
- **Serve results via Flask API** → `app.py`
- **Load models** → `models/`

## 🔧 Configuration

- Default profiling duration: 60 seconds
- Default sampling interval: 1 second
- Max upload file size: 16MB
- Models location: `models/`
- Data location: `data/`

