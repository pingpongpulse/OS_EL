#!/usr/bin/env python
"""Test script to verify all changes work correctly."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.anomaly_detector import AnomalyDetector
from backend.deadlock_detector_new import DeadlockDetector

print("=" * 60)
print("Testing PhaseSentinel Changes")
print("=" * 60)

# Test 1: Anomaly Detector with Anomaly Types
print("\n1. Testing Anomaly Detector with Anomaly Types")
print("-" * 60)

detector = AnomalyDetector()
test_metrics = [
    {'cpu_percent': 98, 'memory_percent': 20, 'memory_used_gb': 1.5, 'disk_read_mb': 5, 'disk_write_mb': 2},
    {'cpu_percent': 25, 'memory_percent': 95, 'memory_used_gb': 7.5, 'disk_read_mb': 10, 'disk_write_mb': 5},
    {'cpu_percent': 50, 'memory_percent': 50, 'memory_used_gb': 3.0, 'disk_read_mb': 1000, 'disk_write_mb': 500},
]

results = detector.detect_anomalies(test_metrics)
print(f"Anomalies detected: {results['anomalies_detected']}")
print(f"Total samples: {results['total_samples']}")

if results.get('alerts'):
    print(f"\nAlerts generated:")
    for i, alert in enumerate(results['alerts'], 1):
        anomaly_type = alert.get('anomaly_type', 'N/A')
        message = alert.get('message', 'N/A')
        severity = alert.get('severity', 'N/A')
        print(f"  {i}. Type: {anomaly_type}, Severity: {severity}")
        print(f"     Message: {message}")

# Test 2: Deadlock Detector
print("\n2. Testing Deadlock Detector with Threading Analysis")
print("-" * 60)

deadlock_detector = DeadlockDetector()
risk_analysis = deadlock_detector.analyze_deadlock_risk()
print(f"Risk Level: {risk_analysis['risk_level']}")
print(f"Has Cycles: {risk_analysis['has_cycles']}")
print(f"Cycle Count: {risk_analysis['cycle_count']}")
print(f"Total Locks Tracked: {risk_analysis['total_locks_tracked']}")

# Test 3: Process Thread Analysis
print("\n3. Testing Process Thread Analysis")
print("-" * 60)

thread_analysis = deadlock_detector.analyze_process_threads()
print(f"Process ID: {thread_analysis['pid']}")
print(f"Process Name: {thread_analysis['process_name']}")
print(f"Thread Count: {thread_analysis['thread_count']}")
print(f"Deadlock Risk: {thread_analysis['deadlock_risk']}")

print("\n" + "=" * 60)
print("All tests completed successfully!")
print("=" * 60)
