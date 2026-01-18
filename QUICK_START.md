# Quick Start Guide - PhaseSentinel Multi-User Data Collection

## What You Can Do Now

Your PhaseSentinel application now **fully supports** collecting data from multiple users and combining it for model training!

## File Structure (Updated)

```
backend/
├── data/
│   ├── training_data.csv          # ✅ Combined training data (merged from all users)
│   ├── user_data/                 # ✅ NEW: User-specific data files
│   │   ├── user_001_external_20240101_120000.csv
│   │   ├── user_002_simulation_20240101_130000.csv
│   │   └── ...
│   ├── optimization_results.csv
│   └── lock_logs.json
├── data_collector.py              # ✅ NEW: Utility for data collection
├── app.py                         # ✅ Updated with API endpoints
└── simulations/
    └── run_simulations.py         # ✅ Fixed syntax error
```

## Three Ways to Collect Data

### 1. Via API Endpoint (Best for Multiple Users)

**Start the server:**
```bash
cd backend
python app.py
```

**Users send data:**
```python
import requests

metrics = [
    {
        'timestamp': 0.0,
        'cpu_percent': 85.5,
        'memory_percent': 30.2,
        'memory_used_gb': 2.1,
        'disk_read_mb': 5.2,
        'disk_write_mb': 2.1,
        'network_sent_mb': 1.0,
        'network_recv_mb': 0.8,
        'phase': 'cpu_bound'
    }
]

response = requests.post('http://localhost:5000/api/collect-data', json={
    'metrics': metrics,
    'user_id': 'user_001',
    'source': 'external',
    'label': 'normal',
    'merge_to_training': False  # Collect first, merge later
})
```

### 2. Using DataCollector Utility

```python
from backend.data_collector import DataCollector

collector = DataCollector()

# Save data from a user
collector.save_user_data(
    metrics=metrics,
    user_id='user_001',
    source='external',
    label='normal'
)

# Merge all user data when ready
collector.merge_all_user_data()
```

### 3. Via Simulations (Already Working)

```bash
cd backend/simulations
python run_simulations.py
```

## New API Endpoints

1. **`POST /api/collect-data`** - Collect data from users
2. **`POST /api/merge-all-data`** - Merge all user data into training_data.csv
3. **`GET /api/user-data-stats`** - Get statistics about collected data

## Workflow

1. **Collect Data from Users**
   - Each user sends data via API → saved to `data/user_data/`
   - Data includes: `user_id`, `source`, `label`, `collection_timestamp`

2. **Review Collected Data**
   ```bash
   curl http://localhost:5000/api/user-data-stats
   ```

3. **Merge All Data**
   ```bash
   curl -X POST http://localhost:5000/api/merge-all-data
   ```
   Or:
   ```python
   from backend.data_collector import DataCollector
   DataCollector().merge_all_user_data()
   ```

4. **Train Models**
   - Use `notebooks/train_models.ipynb`
   - Train on `backend/data/training_data.csv` (now contains all user data)

## Example: Collect from Multiple Users

```python
import requests

# User 1 sends data
requests.post('http://localhost:5000/api/collect-data', json={
    'metrics': user1_metrics,
    'user_id': 'user_001',
    'source': 'external',
    'label': 'normal'
})

# User 2 sends data
requests.post('http://localhost:5000/api/collect-data', json={
    'metrics': user2_metrics,
    'user_id': 'user_002',
    'source': 'external',
    'label': 'anomaly'
})

# Merge all data
requests.post('http://localhost:5000/api/merge-all-data')

# Check stats
stats = requests.get('http://localhost:5000/api/user-data-stats').json()
print(f"Total samples: {stats['stats']['main_training_samples']}")
```

## What Changed

✅ **Added** `/api/collect-data` endpoint for multi-user data collection  
✅ **Added** `/api/merge-all-data` endpoint to combine all user data  
✅ **Added** `/api/user-data-stats` endpoint for data statistics  
✅ **Created** `data_collector.py` utility class  
✅ **Fixed** syntax error in `run_simulations.py`  
✅ **Updated** file structure to support `data/user_data/` directory  
✅ **Added** `requests` to requirements.txt  

## Next Steps

1. **Start collecting data** from your users using the API endpoints
2. **Review** the collected data using `/api/user-data-stats`
3. **Merge** all data when ready using `/api/merge-all-data`
4. **Train** your models using the combined `training_data.csv`

See `COLLECTING_DATA.md` for detailed documentation!


