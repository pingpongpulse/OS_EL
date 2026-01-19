#!/usr/bin/env python3
"""
Test script to verify dashboard integration
Tests the complete data flow from backend API to frontend display
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_dashboard_endpoint():
    """Test /api/dashboard endpoint"""
    print("\n[TEST] Testing /api/dashboard endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard")
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response format: {type(data)}")
        
        # Verify structure
        assert "success" in data, "Missing 'success' field"
        assert "profile_id" in data, "Missing 'profile_id' field"
        assert "data" in data, "Missing 'data' field"
        
        dashboard_data = data["data"]
        assert "metrics" in dashboard_data, "Missing 'metrics' in data"
        assert "phases" in dashboard_data, "Missing 'phases' in data"
        assert "bottlenecks" in dashboard_data, "Missing 'bottlenecks' in data"
        
        # Verify metrics structure
        metrics = dashboard_data["metrics"]
        assert "timestamps" in metrics, "Missing 'timestamps' in metrics"
        assert "cpu" in metrics, "Missing 'cpu' in metrics"
        assert "memory" in metrics, "Missing 'memory' in metrics"
        assert "io" in metrics, "Missing 'io' in metrics"
        
        print(f"✅ Data structure valid")
        print(f"   - Metrics: {len(metrics['timestamps'])} data points")
        print(f"   - Phases: {len(dashboard_data['phases'])} phases detected")
        print(f"   - Bottlenecks: {dashboard_data['bottlenecks']}")
        
        # Verify data consistency
        assert len(metrics["timestamps"]) == len(metrics["cpu"]), "CPU data length mismatch"
        assert len(metrics["timestamps"]) == len(metrics["memory"]), "Memory data length mismatch"
        assert len(metrics["timestamps"]) == len(metrics["io"]), "I/O data length mismatch"
        
        print(f"✅ Data consistency verified")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_dashboard_page():
    """Test dashboard page loads"""
    print("\n[TEST] Testing dashboard page...")
    try:
        response = requests.get(f"{BASE_URL}/dashboard")
        response.raise_for_status()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Content length: {len(response.text)} bytes")
        
        # Check for required elements
        assert "metricsChart" in response.text, "Missing metricsChart canvas"
        assert "phaseChart" in response.text, "Missing phaseChart canvas"
        assert "refresh-btn" in response.text, "Missing refresh button"
        
        print(f"✅ HTML structure valid")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_static_files():
    """Test static file loads"""
    print("\n[TEST] Testing static files...")
    
    files = [
        "/static/js/charts.js",
        "/static/css/style.css"
    ]
    
    all_ok = True
    for file_path in files:
        try:
            response = requests.get(f"{BASE_URL}{file_path}")
            response.raise_for_status()
            print(f"✅ {file_path}: {len(response.text)} bytes")
        except Exception as e:
            print(f"❌ {file_path}: {e}")
            all_ok = False
    
    return all_ok

def main():
    print("=" * 60)
    print("Dashboard Integration Test Suite")
    print("=" * 60)
    
    results = {
        "Dashboard API": test_dashboard_endpoint(),
        "Dashboard Page": test_dashboard_page(),
        "Static Files": test_static_files()
    }
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Dashboard integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
