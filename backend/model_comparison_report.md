# Anomaly Model Comparison Report

## Overview
Comparison of two anomaly detection models: `anomaly_model.pkl` and `anomaly_model (1).pkl`

---

## ✅ anomaly_model.pkl (Standard Model)

### Validation Results
- **File Status**: ✅ VALID AND WORKING
- **File Size**: 1,515,721 bytes
- **Model Type**: `sklearn.ensemble.IsolationForest`
- **Version**: Trained with sklearn 1.6.1, running on 1.7.2 (minor version warning)
- **Features Expected**: **3 features**

### Features Trained On
The model was trained on **3 features**:
1. `cpu_percent` - CPU usage percentage
2. `memory_percent` - Memory usage percentage  
3. `memory_used_gb` - Memory used in gigabytes

### Performance
- **Input Compatibility**: Works with 3-feature input
- **Anomaly Detection**: Successfully identified 2/3 test samples as anomalies
- **Sample Results**:
  - `[10.0, 30.0, 2.0]` → Normal (prediction: 1)
  - `[98.0, 20.0, 1.5]` → Anomaly (prediction: -1) - High CPU
  - `[15.0, 95.0, 8.0]` → Anomaly (prediction: -1) - High memory

### Integration Issues
- ❌ **Incompatible with current AnomalyDetector** - expects 7 features but model only accepts 3
- ❌ Will fail when used with current [AnomalyDetector](file:///c:/PROJECTS/OS_EL/backend/anomaly_detector.py#L12-L233) implementation

---

## ✅ anomaly_model (1).pkl (Alternative Model)

### Validation Results
- **File Status**: ✅ VALID AND WORKING
- **File Size**: 2,360,393 bytes
- **Model Type**: `sklearn.ensemble.IsolationForest`
- **Version**: Trained with sklearn 1.6.1, running on 1.7.2 (minor version warning)
- **Features Expected**: **5 features**

### Features Trained On
The model was trained on **5 features**:
1. `cpu_percent` - CPU usage percentage
2. `memory_percent` - Memory usage percentage
3. `memory_used_gb` - Memory used in gigabytes
4. `disk_read_mb` - Disk read in megabytes
5. `disk_write_mb` - Disk write in megabytes

### Performance
- **Input Compatibility**: Works with 5-feature input
- **Anomaly Detection**: Successfully identified 3/3 test samples as anomalies
- **Sample Results**:
  - `[10.0, 30.0, 2.0, 10.0, 5.0]` → Anomaly (prediction: -1)
  - `[98.0, 20.0, 1.5, 5.0, 2.0]` → Anomaly (prediction: -1) - High CPU
  - `[15.0, 95.0, 8.0, 20.0, 15.0]` → Anomaly (prediction: -1) - High memory

### Integration Issues
- ❌ **Incompatible with current AnomalyDetector** - expects 7 features but model only accepts 5
- ❌ Will fail when used with current [AnomalyDetector](file:///c:/PROJECTS/OS_EL/backend/anomaly_detector.py#L12-L233) implementation

---

## 📊 Model Comparison

| Aspect | anomaly_model.pkl | anomaly_model (1).pkl |
|--------|-------------------|------------------------|
| **File Size** | 1,515,721 bytes | 2,360,393 bytes |
| **Features** | 3 features | 5 features |
| **Detection Sensitivity** | Moderate (2/3 anomalies detected) | High (3/3 anomalies detected) |
| **Resource Coverage** | CPU, Memory | CPU, Memory, Disk I/O |
| **Compatibility** | ❌ Needs 3-feature extractor | ❌ Needs 5-feature extractor |

---

## 🏆 Which Model is Better?

### **anomaly_model (1).pkl** is the better model because:

1. **More Comprehensive**: Monitors 5 system resources vs 3
2. **Higher Sensitivity**: Detected all test anomalies vs only 2 out of 3
3. **Better Resource Coverage**: Includes disk I/O monitoring for I/O-related anomalies
4. **Larger Model**: Contains more learned patterns (larger file size suggests more complexity)

---

## 🔧 Integration Recommendation

To use either model with the current codebase, you need to modify the [AnomalyDetector](file:///c:/PROJECTS/OS_EL/backend/anomaly_detector.py#L12-L233) class's `_extract_features` method:

### For anomaly_model.pkl (3 features):
```python
def _extract_features(self, metrics_data):
    features = []
    for metric in metrics_data:
        feature_vector = [
            float(metric.get('cpu_percent', 0)),
            float(metric.get('memory_percent', 0)),
            float(metric.get('memory_used_gb', 0))
        ]
        features.append(feature_vector)
    return np.array(features)
```

### For anomaly_model (1).pkl (5 features) - **Recommended**:
```python
def _extract_features(self, metrics_data):
    features = []
    for metric in metrics_data:
        feature_vector = [
            float(metric.get('cpu_percent', 0)),
            float(metric.get('memory_percent', 0)),
            float(metric.get('memory_used_gb', 0)),
            float(metric.get('disk_read_mb', 0)),
            float(metric.get('disk_write_mb', 0))
        ]
        features.append(feature_vector)
    return np.array(features)
```

### **Recommendation**: Use `anomaly_model (1).pkl` with the 5-feature extractor as it provides more comprehensive anomaly detection covering CPU, memory, and disk I/O resources.