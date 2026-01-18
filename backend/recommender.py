"""
Optimization Recommender for PhaseSentinel.
Provides optimization recommendations with predicted speedup using regression model.
"""

import os
import joblib
import numpy as np
from datetime import datetime


class OptimizationRecommender:
    """Provides optimization recommendations with speedup predictions."""
    
    def __init__(self, model_path='models/regression_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.model_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Load the regression model if it exists."""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                self.model_loaded = True
                print(f"Regression model loaded from {self.model_path}")
            except Exception as e:
                print(f"Error loading regression model: {e}")
                self.model_loaded = False
        else:
            print(f"Regression model not found at {self.model_path}")
            print("Model not loaded - using placeholder logic")
            self.model_loaded = False
    
    def recommend(self, bottlenecks, anomalies):
        """Flask-compatible recommend() method."""
        if not bottlenecks:
            return []
        
        recommendations = []
        for bottleneck in bottlenecks:
            phase_type = self._infer_phase_type_from_bottleneck(bottleneck)
            recommendations.append({
                'bottleneck_type': bottleneck.get('type', 'unknown'),
                'phase_type': phase_type,
                'predicted_speedup': self._estimate_speedup(phase_type),
                'suggestions': self._get_phase_specific_recommendations(phase_type)
            })
        
        return recommendations
    
    def _infer_phase_type_from_bottleneck(self, bottleneck):
        """Infer phase type from bottleneck data."""
        bottleneck_type = bottleneck.get('type', '').lower()
        if 'cpu' in bottleneck_type:
            return 'cpu_bound'
        elif 'memory' in bottleneck_type:
            return 'memory_bound'
        elif 'i/o' in bottleneck_type or 'io' in bottleneck_type:
            return 'io_bound'
        else:
            return 'mixed'
    
    def get_recommendations(self, metrics_data, phase_type=None):
        """
        Get optimization recommendations with predicted speedup.
        
        Args:
            metrics_data: List of metric dictionaries or single metric dict
            phase_type: Type of phase (cpu_bound, io_bound, memory_bound, etc.)
            
        Returns:
            dict: Recommendations with predicted speedup
        """
        if not self.model_loaded:
            return self._placeholder_recommendations(metrics_data, phase_type)
        
        try:
            # Convert metrics to feature array if needed
            if isinstance(metrics_data, dict):
                features = self._extract_features([metrics_data])
            elif isinstance(metrics_data, list):
                features = self._extract_features(metrics_data)
            else:
                features = metrics_data
            
            # Predict speedup using the model
            speedup_predictions = self.model.predict(features)
            
            # Generate recommendations based on predictions
            recommendations = []
            for idx, speedup in enumerate(speedup_predictions):
                speedup_value = float(speedup)
                improvement_pct = (speedup_value - 1.0) * 100
                
                # Determine phase type if not provided
                if phase_type is None:
                    phase_type = self._infer_phase_type(metrics_data[idx] if isinstance(metrics_data, list) else metrics_data)
                
                rec = {
                    'phase_type': phase_type,
                    'predicted_speedup': speedup_value,
                    'predicted_improvement_pct': improvement_pct,
                    'recommendations': self._get_phase_specific_recommendations(phase_type),
                    'confidence': 'high' if abs(improvement_pct) > 10 else 'medium'
                }
                recommendations.append(rec)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'model_loaded': True,
                'recommendations': recommendations,
                'average_speedup': float(np.mean(speedup_predictions)),
                'max_speedup': float(np.max(speedup_predictions))
            }
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'model_loaded': True,
                'error': str(e),
                'recommendations': []
            }
    
    def _placeholder_recommendations(self, metrics_data, phase_type=None):
        """
        Placeholder recommendations using rule-based logic.
        Used when model is not available.
        """
        if isinstance(metrics_data, dict):
            metrics_data = [metrics_data]
        
        if not metrics_data:
            return {
                'timestamp': datetime.now().isoformat(),
                'model_loaded': False,
                'recommendations': [],
                'warning': 'No metrics data provided'
            }
        
        recommendations = []
        
        for metric in metrics_data:
            # Infer phase type if not provided
            if phase_type is None:
                phase_type = self._infer_phase_type(metric)
            
            # Generate rule-based recommendations
            rec = {
                'phase_type': phase_type,
                'predicted_speedup': self._estimate_speedup(phase_type),
                'predicted_improvement_pct': (self._estimate_speedup(phase_type) - 1.0) * 100,
                'recommendations': self._get_phase_specific_recommendations(phase_type),
                'confidence': 'low',
                'note': 'Using placeholder logic. Model not loaded - consider training regression_model.pkl for accurate predictions.'
            }
            recommendations.append(rec)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'model_loaded': False,
            'recommendations': recommendations,
            'average_speedup': np.mean([r['predicted_speedup'] for r in recommendations]),
            'warning': 'Model not loaded - using placeholder predictions'
        }
    
    def _infer_phase_type(self, metric):
        """Infer phase type from metrics."""
        cpu = float(metric.get('cpu_percent', 0))
        memory = float(metric.get('memory_percent', 0))
        disk_read = float(metric.get('disk_read_mb', 0))
        disk_write = float(metric.get('disk_write_mb', 0))
        io_rate = disk_read + disk_write
        
        if cpu < 10 and memory < 30:
            return 'idle'
        elif cpu > 70:
            return 'cpu_bound'
        elif io_rate > 10:
            return 'io_bound'
        elif memory > 70:
            return 'memory_bound'
        else:
            return 'mixed'
    
    def _estimate_speedup(self, phase_type):
        """Estimate speedup based on phase type (placeholder)."""
        estimates = {
            'cpu_bound': 1.5,  # 50% improvement
            'io_bound': 2.0,   # 100% improvement
            'memory_bound': 1.3,  # 30% improvement
            'mixed': 1.2,      # 20% improvement
            'idle': 1.0        # No improvement
        }
        return estimates.get(phase_type, 1.1)
    
    def _get_phase_specific_recommendations(self, phase_type):
        """Get specific optimization recommendations for phase type."""
        recommendations_map = {
            'cpu_bound': [
                'Consider parallelization using multiprocessing or threading',
                'Profile code with cProfile to identify CPU hotspots',
                'Use optimized libraries (NumPy, Cython) for computational tasks',
                'Consider algorithm optimization (reduce time complexity)',
                'Use vectorization instead of loops where possible'
            ],
            'io_bound': [
                'Implement asynchronous I/O operations (asyncio)',
                'Use connection pooling for database operations',
                'Implement caching for frequently accessed data',
                'Consider using faster storage (SSD) or in-memory databases',
                'Batch I/O operations to reduce overhead'
            ],
            'memory_bound': [
                'Optimize data structures to reduce memory footprint',
                'Implement memory pooling for frequently allocated objects',
                'Use generators instead of lists for large datasets',
                'Consider garbage collection tuning',
                'Profile memory usage with memory_profiler'
            ],
            'mixed': [
                'Profile both CPU and I/O to identify primary bottleneck',
                'Consider refactoring to separate CPU-intensive and I/O-intensive phases',
                'Apply multiple optimization strategies',
                'Use profiling tools to identify the most impactful optimizations'
            ],
            'idle': [
                'System is idle - no optimization needed',
                'Consider if profiling duration was sufficient',
                'Check if program is waiting for external resources'
            ]
        }
        
        return recommendations_map.get(phase_type, [
            'Review code for optimization opportunities',
            'Use profiling tools to identify bottlenecks'
        ])
    
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
                float(metric.get('disk_write_mb', 0)),
                float(metric.get('network_sent_mb', 0)),
                float(metric.get('network_recv_mb', 0))
            ]
            features.append(feature_vector)
        
        return np.array(features)


if __name__ == '__main__':
    # Test the recommender
    recommender = OptimizationRecommender()
    
    # Test with sample data
    test_metrics = [
        {'cpu_percent': 85, 'memory_percent': 30, 'memory_used_gb': 2.0,
         'disk_read_mb': 5, 'disk_write_mb': 2, 'network_sent_mb': 1, 'network_recv_mb': 1},
        {'cpu_percent': 20, 'memory_percent': 80, 'memory_used_gb': 6.0,
         'disk_read_mb': 10, 'disk_write_mb': 8, 'network_sent_mb': 2, 'network_recv_mb': 2}
    ]
    
    results = recommender.get_recommendations(test_metrics)
    print(f"\nOptimization Recommendations:")
    print(f"Model loaded: {results['model_loaded']}")
    print(f"Average speedup: {results.get('average_speedup', 'N/A'):.2f}x")
    print(f"\nRecommendations:")
    for idx, rec in enumerate(results['recommendations']):
        print(f"\n  Phase {idx + 1} ({rec['phase_type']}):")
        print(f"    Predicted speedup: {rec['predicted_speedup']:.2f}x ({rec['predicted_improvement_pct']:.1f}% improvement)")
        print(f"    Recommendations:")
        for recommendation in rec['recommendations']:
            print(f"      - {recommendation}")


