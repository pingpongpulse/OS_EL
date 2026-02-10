"""
Security Anomaly Detector for PhaseSentinel.
Updated implementation that loads anomaly_model.pkl with 5-feature compatibility.
"""

import os
import joblib
import numpy as np
from datetime import datetime


class AnomalyDetector:
    """Detects security anomalies using a pre-trained model."""
    
    def __init__(self, model_path=None):
        # Use absolute path based on module location
        if model_path is None:
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(backend_dir, 'models', 'anomaly_model.pkl')
        self.model_path = model_path
        self.model = None
        self.model_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Load the anomaly detection model if it exists."""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                self.model_loaded = True
                print(f"Anomaly model loaded from {self.model_path}")
            except Exception as e:
                print(f"Error loading anomaly model: {e}")
                self.model_loaded = False
        else:
            print(f"Anomaly model not found at {self.model_path}")
            print("Model not loaded - using placeholder logic")
            self.model_loaded = False
    
    def detect(self, metrics):
        """Flask-compatible detect() method for PhaseSentinel."""
        return self.detect_anomalies(metrics)
    
    def detect_anomalies(self, metrics_data):
        """
        Detect security anomalies in metrics data.
        
        Args:
            metrics_data: List of dictionaries containing metrics, or numpy array
            
        Returns:
            dict: Anomaly detection results
        """
        if not self.model_loaded:
            return self._placeholder_detection(metrics_data)
        
        try:
            # Convert metrics to feature array if needed
            if isinstance(metrics_data, list):
                features = self._extract_features(metrics_data)
            else:
                features = metrics_data
            
            # Predict anomalies using the model
            predictions = self.model.predict(features)
            anomaly_scores = None
            
            # Get anomaly scores if available (Isolation Forest, etc.)
            if hasattr(self.model, 'decision_function'):
                anomaly_scores = self.model.decision_function(features)
            elif hasattr(self.model, 'score_samples'):
                anomaly_scores = self.model.score_samples(features)
            
            # Identify anomalous samples
            anomalous_indices = np.where(predictions == -1)[0] if hasattr(predictions, '__iter__') else []
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'model_loaded': True,
                'total_samples': len(features) if hasattr(features, '__len__') else 1,
                'anomalies_detected': len(anomalous_indices),
                'anomalous_indices': anomalous_indices.tolist() if len(anomalous_indices) > 0 else [],
                'anomaly_scores': anomaly_scores.tolist() if anomaly_scores is not None else None,
                'alerts': self._generate_alerts(anomalous_indices, anomaly_scores, metrics_data)
            }
            
            return results
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'model_loaded': True,
                'error': str(e),
                'anomalies_detected': 0,
                'alerts': [{
                    'type': 'error',
                    'message': f'Error during anomaly detection: {e}'
                }]
            }
    
    def _placeholder_detection(self, metrics_data):
        """
        Placeholder anomaly detection using rule-based logic.
        Used when model is not available.
        """
        if isinstance(metrics_data, list) and len(metrics_data) == 0:
            return {
                'timestamp': datetime.now().isoformat(),
                'model_loaded': False,
                'total_samples': 0,
                'anomalies_detected': 0,
                'alerts': [{
                    'type': 'info',
                    'message': 'No metrics data provided'
                }]
            }
        
        alerts = []
        anomalies_detected = 0
        
        # Rule-based anomaly detection
        if isinstance(metrics_data, list):
            for idx, metric in enumerate(metrics_data):
                # Check for suspicious CPU usage (crypto mining pattern)
                cpu = float(metric.get('cpu_percent', 0))
                if cpu > 95:
                    alerts.append({
                        'type': 'warning',
                        'message': f'Sample {idx}: Extremely high CPU usage ({cpu:.1f}%) - possible crypto mining activity',
                        'sample_index': idx,
                        'severity': 'high'
                    })
                    anomalies_detected += 1
                
                # Check for memory leak pattern
                memory = float(metric.get('memory_percent', 0))
                if memory > 90:
                    alerts.append({
                        'type': 'warning',
                        'message': f'Sample {idx}: Critical memory usage ({memory:.1f}%) - possible memory leak',
                        'sample_index': idx,
                        'severity': 'high'
                    })
                    anomalies_detected += 1
                
                # Check for unusual I/O patterns
                disk_read = float(metric.get('disk_read_mb', 0))
                disk_write = float(metric.get('disk_write_mb', 0))
                if disk_read > 1000 or disk_write > 1000:
                    alerts.append({
                        'type': 'warning',
                        'message': f'Sample {idx}: Unusual I/O activity (Read: {disk_read:.1f}MB, Write: {disk_write:.1f}MB)',
                        'sample_index': idx,
                        'severity': 'medium'
                    })
                    anomalies_detected += 1
        
        if anomalies_detected == 0:
            alerts.append({
                'type': 'info',
                'message': 'No anomalies detected using rule-based detection. Model not loaded - consider training anomaly_model.pkl for better detection.'
            })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'model_loaded': False,
            'total_samples': len(metrics_data) if isinstance(metrics_data, list) else 1,
            'anomalies_detected': anomalies_detected,
            'alerts': alerts,
            'warning': 'Using placeholder detection. Model not loaded.'
        }
    
    def _extract_features(self, metrics_data):
        """
        Extract features from metrics data for model input.
        
        Args:
            metrics_data: List of metric dictionaries
            
        Returns:
            numpy.ndarray: Feature matrix
        """
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
    
    def _generate_alerts(self, anomalous_indices, anomaly_scores, metrics_data):
        """Generate alert messages for detected anomalies."""
        alerts = []
        
        if len(anomalous_indices) == 0:
            alerts.append({
                'type': 'info',
                'message': 'No security anomalies detected'
            })
            return alerts
        
        for idx in anomalous_indices:
            score = None
            if anomaly_scores is not None and idx < len(anomaly_scores):
                score = float(anomaly_scores[idx])
            
            alert = {
                'type': 'warning',
                'message': f'Security anomaly detected in sample {idx}',
                'sample_index': int(idx),
                'severity': 'high' if score and score < -0.5 else 'medium'
            }
            
            if score is not None:
                alert['anomaly_score'] = score
            
            if isinstance(metrics_data, list) and idx < len(metrics_data):
                metric = metrics_data[idx]
                alert['details'] = {
                    'cpu_percent': metric.get('cpu_percent', 'N/A'),
                    'memory_percent': metric.get('memory_percent', 'N/A')
                }
            
            alerts.append(alert)
        
        return alerts


if __name__ == '__main__':
    # Test the anomaly detector
    detector = AnomalyDetector()
    
    # Test with sample data
    test_metrics = [
        {'cpu_percent': 10, 'memory_percent': 30, 'memory_used_gb': 2.0,
         'disk_read_mb': 10, 'disk_write_mb': 5},
        {'cpu_percent': 98, 'memory_percent': 20, 'memory_used_gb': 1.5,
         'disk_read_mb': 5, 'disk_write_mb': 2},
        {'cpu_percent': 15, 'memory_percent': 95, 'memory_used_gb': 8.0,
         'disk_read_mb': 20, 'disk_write_mb': 15}
    ]
    
    results = detector.detect_anomalies(test_metrics)
    print(f"\nAnomaly Detection Results:")
    print(f"Model loaded: {results['model_loaded']}")
    print(f"Anomalies detected: {results['anomalies_detected']}")
    print(f"\nAlerts:")
    for alert in results['alerts']:
        print(f"  [{alert['type'].upper()}] {alert['message']}")


