# Collecting Data from Multiple Users - PhaseSentinel

This guide explains how to collect metrics data from multiple users and combine it for model training.

## File Structure Support

The current structure **fully supports** multi-user data collection:

```
backend/
├── data/
│   ├── training_data.csv          # Combined training data (merged from all users)
│   ├── user_data/                  # User-specific data files
│   │   ├── user_001_external_20240101_120000.csv
│   │   ├── user_002_simulation_20240101_130000.csv
│   │   └── user_003_web_20240101_140000.csv
│   ├── optimization_results.csv
│   └── lock_logs.json
├── data_collector.py               # Utility for data collection
└── app.py                          # API endpoints for data collection
```

## Methods for Data Collection

### Method 1: API Endpoint (Recommended for Multiple Users)

Users can send data via HTTP POST request:

```python
import requests

# Example: Send metrics data from a user
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
    },
    # ... more metrics
]

response = requests.post('http://your-server:5000/api/collect-data', json={
    'metrics': metrics,
    'user_id': 'user_001',
    'source': 'external',  # 'external', 'simulation', 'web'
    'label': 'normal',     # 'normal', 'anomaly', etc.
    'merge_to_training': False  # Set True to auto-merge
})

print(response.json())
```

**API Endpoint:** `POST /api/collect-data`

**Request Body:**
```json
{
    "metrics": [...],           // Array of metric dictionaries
    "user_id": "user_001",      // Unique user identifier
    "source": "external",        // Data source type
    "label": "normal",          // Data label
    "merge_to_training": false  // Auto-merge option
}
```

### Method 2: Using DataCollector Utility

```python
from backend.data_collector import DataCollector

collector = DataCollector(data_dir='backend/data')

# Save data from a user
file_path = collector.save_user_data(
    metrics=metrics,
    user_id='user_001',
    source='external',
    label='normal',
    merge_to_training=False  # Save separately first
)

# Later, merge all user data
merged_count = collector.merge_all_user_data()
print(f"Merged {merged_count} user data files")
```

### Method 3: Direct CSV Upload (Manual)

Users can create CSV files with the following format:

```csv
timestamp,cpu_percent,memory_percent,memory_used_gb,disk_read_mb,disk_write_mb,network_sent_mb,network_recv_mb,phase,user_id,source,label
0.0,85.5,30.2,2.1,5.2,2.1,1.0,0.8,cpu_bound,user_001,external,normal
```

Place files in `backend/data/user_data/` directory.

## Merging Data from Multiple Users

### Option 1: Auto-merge on Collection

Set `merge_to_training: true` when sending data via API:

```python
response = requests.post('/api/collect-data', json={
    'metrics': metrics,
    'user_id': 'user_001',
    'merge_to_training': True  # Auto-merge immediately
})
```

### Option 2: Manual Merge via API

```python
# Merge all user data files
response = requests.post('http://your-server:5000/api/merge-all-data')
print(response.json())
```

### Option 3: Merge via Utility Script

```python
from backend.data_collector import DataCollector

collector = DataCollector()
merged_count = collector.merge_all_user_data()
print(f"Merged {merged_count} files into training_data.csv")
```

## Checking Data Statistics

### Via API

```python
response = requests.get('http://your-server:5000/api/user-data-stats')
stats = response.json()
print(stats)
```

### Via Utility

```python
from backend.data_collector import DataCollector

collector = DataCollector()
stats = collector.get_stats()
print(f"User files: {stats['user_files']}")
print(f"Total samples: {stats['total_user_samples']}")
print(f"Users: {list(stats['users'].keys())}")
```

## Workflow for Multi-User Data Collection

1. **Start Flask Server**
   ```bash
   cd backend
   python app.py
   ```

2. **Users Send Data**
   - Each user sends metrics via `/api/collect-data`
   - Data is saved to `data/user_data/user_{id}_{source}_{timestamp}.csv`

3. **Review Collected Data**
   ```bash
   # Check statistics
   curl http://localhost:5000/api/user-data-stats
   ```

4. **Merge All Data**
   ```bash
   # Via API
   curl -X POST http://localhost:5000/api/merge-all-data
   
   # Or via Python
   python -c "from backend.data_collector import DataCollector; DataCollector().merge_all_user_data()"
   ```

5. **Train Models**
   - Use `notebooks/train_models.ipynb`
   - Train on `backend/data/training_data.csv`

## Example: Complete Data Collection Script

```python
import requests
import json

# Collect data from multiple users
users_data = [
    {
        'user_id': 'user_001',
        'metrics': [...],  # Your metrics here
        'label': 'normal'
    },
    {
        'user_id': 'user_002',
        'metrics': [...],
        'label': 'anomaly'
    }
]

# Send data for each user
for user_data in users_data:
    response = requests.post('http://localhost:5000/api/collect-data', json={
        'metrics': user_data['metrics'],
        'user_id': user_data['user_id'],
        'source': 'external',
        'label': user_data['label'],
        'merge_to_training': False  # Collect first, merge later
    })
    print(f"User {user_data['user_id']}: {response.json()}")

# Merge all collected data
merge_response = requests.post('http://localhost:5000/api/merge-all-data')
print(f"Merged: {merge_response.json()}")

# Check final statistics
stats_response = requests.get('http://localhost:5000/api/user-data-stats')
print(f"Final stats: {stats_response.json()}")
```

## Data Format Requirements

Each metric dictionary should contain:

```python
{
    'timestamp': float,           # Time since start (seconds)
    'cpu_percent': float,         # CPU usage percentage
    'memory_percent': float,      # Memory usage percentage
    'memory_used_gb': float,      # Memory used in GB
    'disk_read_mb': float,        # Disk read in MB
    'disk_write_mb': float,       # Disk write in MB
    'network_sent_mb': float,     # Network sent in MB
    'network_recv_mb': float,      # Network received in MB
    'phase': str                  # Phase type: 'cpu_bound', 'io_bound', 'memory_bound', 'idle', 'mixed'
}
```

Optional metadata (added automatically):
- `user_id`: User identifier
- `source`: Data source ('external', 'simulation', 'web')
- `label`: Data label ('normal', 'anomaly', etc.)
- `collection_timestamp`: ISO timestamp of collection

## Next Steps

1. **Collect Data**: Use API endpoints or utility scripts to collect data from users
2. **Review Data**: Check statistics and data quality
3. **Merge Data**: Combine all user data into `training_data.csv`
4. **Train Models**: Use `notebooks/train_models.ipynb` to train models
5. **Deploy**: Models will be automatically loaded by the application


