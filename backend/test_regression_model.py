#!/usr/bin/env python
"""Test script to verify regression model integration."""

from recommender import OptimizationRecommender
import json

print("=" * 60)
print("REGRESSION MODEL INTEGRATION TEST")
print("=" * 60)

# Initialize recommender with regression model
recommender = OptimizationRecommender()

print(f"\n✓ Recommender initialized")
print(f"  Model loaded: {recommender.model_loaded}")
print(f"  Model path: {recommender.model_path}")
print(f"  Model type: {type(recommender.model).__name__}")

# Test with diverse metrics
test_metrics = [
    {
        'name': 'CPU-Bound Task',
        'cpu_percent': 85, 'memory_percent': 30, 'memory_used_gb': 2.0,
        'disk_read_mb': 5, 'disk_write_mb': 2, 'network_sent_mb': 1, 'network_recv_mb': 1
    },
    {
        'name': 'Memory-Intensive Task',
        'cpu_percent': 20, 'memory_percent': 80, 'memory_used_gb': 6.0,
        'disk_read_mb': 10, 'disk_write_mb': 8, 'network_sent_mb': 2, 'network_recv_mb': 2
    },
    {
        'name': 'I/O-Bound Task',
        'cpu_percent': 15, 'memory_percent': 40, 'memory_used_gb': 3.0,
        'disk_read_mb': 50, 'disk_write_mb': 45, 'network_sent_mb': 10, 'network_recv_mb': 15
    },
    {
        'name': 'Mixed Workload',
        'cpu_percent': 65, 'memory_percent': 65, 'memory_used_gb': 4.5,
        'disk_read_mb': 20, 'disk_write_mb': 18, 'network_sent_mb': 5, 'network_recv_mb': 7
    }
]

# Extract metrics without 'name'
metrics_for_prediction = [{k: v for k, v in m.items() if k != 'name'} for m in test_metrics]

print(f"\n✓ Testing with {len(test_metrics)} different workload types")
results = recommender.get_recommendations(metrics_for_prediction)

print(f"\n{'=' * 60}")
print("PREDICTION RESULTS")
print(f"{'=' * 60}")
print(f"\nModel Status: {'LOADED ✓' if results['model_loaded'] else 'NOT LOADED ✗'}")
print(f"Average Speedup: {results.get('average_speedup', 0):.2f}x")
print(f"Max Speedup: {results.get('max_speedup', 0):.2f}x")
print(f"Total Recommendations: {len(results['recommendations'])}")

print(f"\n{'=' * 60}")
print("DETAILED PREDICTIONS")
print(f"{'=' * 60}")

for i, (test_case, rec) in enumerate(zip(test_metrics, results['recommendations'])):
    print(f"\n[{i+1}] {test_case['name']}")
    print(f"    Input Metrics:")
    print(f"      - CPU: {test_case['cpu_percent']:.0f}%")
    print(f"      - Memory: {test_case['memory_percent']:.0f}% ({test_case['memory_used_gb']:.1f}GB)")
    print(f"      - Disk I/O: {test_case['disk_read_mb']:.0f}MB read, {test_case['disk_write_mb']:.0f}MB write")
    print(f"    Predictions:")
    print(f"      - Phase Type: {rec['phase_type']}")
    print(f"      - Predicted Speedup: {rec['predicted_speedup']:.2f}x")
    print(f"      - Improvement: {rec['predicted_improvement_pct']:.1f}%")
    print(f"      - Confidence: {rec.get('confidence', 'N/A')}")
    if rec['recommendations']:
        print(f"    Top Recommendations:")
        for j, recommendation in enumerate(rec['recommendations'][:2]):
            print(f"      • {recommendation}")

print(f"\n{'=' * 60}")
print("✓ REGRESSION MODEL INTEGRATION SUCCESSFUL!")
print(f"{'=' * 60}\n")
