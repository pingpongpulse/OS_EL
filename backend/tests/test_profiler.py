"""
Unit tests for PhaseProfiler.
Tests metric collection and phase detection functionality.
"""

import unittest
import os
import sys
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phaseprofiler import PhaseProfiler


class TestPhaseProfiler(unittest.TestCase):
    """Test cases for PhaseProfiler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.temp_dir, 'test_metrics.csv')
        self.profiler = PhaseProfiler(output_file=self.output_file)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_phase_detection_idle(self):
        """Test phase detection for idle state."""
        phase = self.profiler.detect_phase(cpu_percent=5.0, memory_percent=20.0, io_rate=0.1)
        self.assertEqual(phase, 'idle')
    
    def test_phase_detection_cpu_bound(self):
        """Test phase detection for CPU-bound workload."""
        phase = self.profiler.detect_phase(cpu_percent=80.0, memory_percent=50.0, io_rate=2.0)
        self.assertEqual(phase, 'cpu_bound')
    
    def test_phase_detection_io_bound(self):
        """Test phase detection for I/O-bound workload."""
        phase = self.profiler.detect_phase(cpu_percent=30.0, memory_percent=50.0, io_rate=50.0)
        self.assertEqual(phase, 'io_bound')
    
    def test_phase_detection_memory_bound(self):
        """Test phase detection for memory-bound workload."""
        phase = self.profiler.detect_phase(cpu_percent=40.0, memory_percent=85.0, io_rate=5.0)
        self.assertEqual(phase, 'memory_bound')
    
    def test_phase_detection_mixed(self):
        """Test phase detection for mixed workload."""
        phase = self.profiler.detect_phase(cpu_percent=60.0, memory_percent=60.0, io_rate=15.0)
        self.assertEqual(phase, 'mixed')
    
    def test_metric_collection(self):
        """Test metric collection functionality."""
        # Collect metrics for a short duration
        metrics = self.profiler.collect_metrics(duration=2, interval=0.5)
        
        # Check that metrics were collected
        self.assertGreater(len(metrics), 0)
        
        # Check metric structure
        sample = metrics[0]
        self.assertIn('timestamp', sample)
        self.assertIn('cpu_percent', sample)
        self.assertIn('memory_percent', sample)
        self.assertIn('phase', sample)
        self.assertIn('sample_id', sample)
    
    def test_save_to_csv(self):
        """Test saving metrics to CSV file."""
        # Collect some metrics first
        self.profiler.collect_metrics(duration=1, interval=0.5)
        
        # Save to CSV
        self.profiler.save_to_csv()
        
        # Check that file was created
        self.assertTrue(os.path.exists(self.output_file))
        
        # Check file content
        with open(self.output_file, 'r') as f:
            lines = f.readlines()
            self.assertGreater(len(lines), 1)  # Header + at least one data row
            
            # Check header
            header = lines[0].strip().split(',')
            expected_fields = ['timestamp', 'cpu_percent', 'memory_percent', 'phase']
            for field in expected_fields:
                self.assertIn(field, header)
    
    def test_save_to_csv_empty_metrics(self):
        """Test saving when no metrics are collected."""
        # Don't collect any metrics
        self.profiler.save_to_csv()
        
        # File should not be created if no metrics
        # (This depends on implementation - adjust if needed)
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r') as f:
                lines = f.readlines()
                self.assertEqual(len(lines), 0)  # Empty file or just header


class TestPhaseProfilerIntegration(unittest.TestCase):
    """Integration tests for PhaseProfiler."""
    
    def test_full_profiling_workflow(self):
        """Test complete profiling workflow: collect -> detect -> save."""
        temp_dir = tempfile.mkdtemp()
        output_file = os.path.join(temp_dir, 'integration_test.csv')
        
        try:
            profiler = PhaseProfiler(output_file=output_file)
            
            # Collect metrics
            metrics = profiler.collect_metrics(duration=1, interval=0.5)
            self.assertGreater(len(metrics), 0)
            
            # Save metrics
            profiler.save_to_csv()
            self.assertTrue(os.path.exists(output_file))
            
            # Verify all metrics have valid phases
            for metric in metrics:
                self.assertIn(metric['phase'], ['idle', 'cpu_bound', 'io_bound', 'memory_bound', 'mixed'])
                
        finally:
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main()

