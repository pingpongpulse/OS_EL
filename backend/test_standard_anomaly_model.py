#!/usr/bin/env python3
"""
Test script to validate if anomaly_model.pkl is valid and working.
"""

import os
import joblib
import numpy as np
import sys

def test_anomaly_model_standard():
    """Test the anomaly_model.pkl file."""
    print("Testing anomaly_model.pkl...")
    
    # Define the path to the model file
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'anomaly_model.pkl')
    
    # Check if file exists
    if not os.path.exists(model_path):
        print(f"❌ Error: Model file not found at {model_path}")
        return False
    
    print(f"✅ Found model file at: {model_path}")
    print(f"📁 File size: {os.path.getsize(model_path)} bytes")
    
    # Try to load the model
    try:
        print("\n🔍 Attempting to load the model...")
        model = joblib.load(model_path)
        print(f"✅ Model loaded successfully!")
        print(f"📊 Model type: {type(model)}")
        
        # Print model attributes if available
        if hasattr(model, 'get_params'):
            params = model.get_params()
            print(f"⚙️  Model parameters: {len(params)} parameters")
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False
    
    # Test the model with sample data
    print("\n🧪 Testing model with sample data...")
    try:
        # Sample feature data (based on the current AnomalyDetector expectations - 7 features)
        sample_data = np.array([
            [10.0, 30.0, 2.0, 10.0, 5.0, 1.0, 1.0],  # Normal usage
            [98.0, 20.0, 1.5, 5.0, 2.0, 0.5, 0.5],  # High CPU (potential anomaly)
            [15.0, 95.0, 8.0, 20.0, 15.0, 2.0, 2.0]  # High memory (potential anomaly)
        ])
        
        print(f"📋 Sample data shape: {sample_data.shape}")
        
        # Test prediction
        predictions = model.predict(sample_data)
        print(f"🎯 Model predictions: {predictions}")
        print(f"📊 Number of anomalies detected: {sum(predictions == -1)}")
        
        # Test if model has decision_function or score_samples
        if hasattr(model, 'decision_function'):
            scores = model.decision_function(sample_data)
            print(f"📈 Decision function scores: {scores}")
        elif hasattr(model, 'score_samples'):
            scores = model.score_samples(sample_data)
            print(f"📈 Score samples: {scores}")
        
        print("✅ Model test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during model testing: {e}")
        # Try with 5 features to see if this is the expected input
        print("\n🔄 Trying with 5 features (in case model expects fewer features)...")
        try:
            sample_data_5 = np.array([
                [10.0, 30.0, 2.0, 10.0, 5.0],  # Normal usage
                [98.0, 20.0, 1.5, 5.0, 2.0],  # High CPU (potential anomaly)
                [15.0, 95.0, 8.0, 20.0, 15.0]  # High memory (potential anomaly)
            ])
            
            print(f"📋 Sample data shape (5 features): {sample_data_5.shape}")
            
            # Test prediction
            predictions = model.predict(sample_data_5)
            print(f"🎯 Model predictions (5 features): {predictions}")
            print(f"📊 Number of anomalies detected: {sum(predictions == -1)}")
            
            # Test if model has decision_function or score_samples
            if hasattr(model, 'decision_function'):
                scores = model.decision_function(sample_data_5)
                print(f"📈 Decision function scores: {scores}")
            elif hasattr(model, 'score_samples'):
                scores = model.score_samples(sample_data_5)
                print(f"📈 Score samples: {scores}")
            
            print("✅ Model test with 5 features completed successfully!")
            return True
            
        except Exception as e2:
            print(f"❌ Error during 5-feature model testing: {e2}")
            return False

def test_with_anomaly_detector_class():
    """Test using the AnomalyDetector class with the standard model file."""
    print("\n🔧 Testing with AnomalyDetector class...")
    
    # Import the AnomalyDetector class
    sys.path.insert(0, os.path.dirname(__file__))
    from anomaly_detector import AnomalyDetector
    
    # Create a standard detector that points to the default model file
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'anomaly_model.pkl')
    
    try:
        # Create detector with the default model path
        detector = AnomalyDetector()  # Uses default path
        print(f"✅ AnomalyDetector initialized with model: {detector.model_loaded}")
        
        if not detector.model_loaded:
            print("⚠️  Standard model not loaded, using placeholder logic")
            return False
        
        # Test with sample data (7 features as expected by current AnomalyDetector)
        test_metrics = [
            {'cpu_percent': 10, 'memory_percent': 30, 'memory_used_gb': 2.0,
             'disk_read_mb': 10, 'disk_write_mb': 5, 'network_sent_mb': 1, 'network_recv_mb': 1},
            {'cpu_percent': 98, 'memory_percent': 20, 'memory_used_gb': 1.5,
             'disk_read_mb': 5, 'disk_write_mb': 2, 'network_sent_mb': 0.5, 'network_recv_mb': 0.5},
            {'cpu_percent': 15, 'memory_percent': 95, 'memory_used_gb': 8.0,
             'disk_read_mb': 20, 'disk_write_mb': 15, 'network_sent_mb': 2, 'network_recv_mb': 2}
        ]
        
        results = detector.detect_anomalies(test_metrics)
        print(f"📊 Anomaly detection results:")
        print(f"   Model loaded: {results['model_loaded']}")
        print(f"   Anomalies detected: {results['anomalies_detected']}")
        
        for alert in results['alerts']:
            print(f"   Alert: [{alert['type'].upper()}] {alert['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing with AnomalyDetector: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting anomaly_model.pkl validation test...\n")
    
    success = test_anomaly_model_standard()
    
    if success:
        test_with_anomaly_detector_class()
    
    print(f"\n🏁 Test completed.")