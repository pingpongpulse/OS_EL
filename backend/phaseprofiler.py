"""
Mono profiler script for PhaseProfiler.
Collects metrics (CPU, I/O, memory), detects phases, and saves to CSV.
"""

import psutil
import time
import csv
import sys
import os
import subprocess
from datetime import datetime
import argparse


class PhaseProfiler:
    """Profiles system metrics and detects execution phases."""
    
    def __init__(self, output_file='training_data.csv'):
        self.output_file = output_file
        self.metrics = []
        self.process = None
        
    def collect_metrics(self, duration=60, interval=1):
        """
        Collect system metrics over specified duration.
        
        Args:
            duration: Time to collect metrics (seconds)
            interval: Sampling interval (seconds)
        """
        print(f"Starting metric collection for {duration} seconds...")
        start_time = time.time()
        sample_count = 0
        
        while time.time() - start_time < duration:
            timestamp = time.time() - start_time
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024**3)  # GB
            memory_available = memory.available / (1024**3)  # GB
            
            # Disk I/O metrics
            disk_io = psutil.disk_io_counters()
            disk_read = disk_io.read_bytes / (1024**2) if disk_io else 0  # MB
            disk_write = disk_io.write_bytes / (1024**2) if disk_io else 0  # MB
            
            # Network I/O (if available)
            net_io = psutil.net_io_counters()
            net_sent = net_io.bytes_sent / (1024**2) if net_io else 0  # MB
            net_recv = net_io.bytes_recv / (1024**2) if net_io else 0  # MB
            
            # Detect phase based on metrics (simple heuristic)
            phase = self.detect_phase(cpu_percent, memory_percent, disk_read + disk_write)
            
            metric = {
                'timestamp': timestamp,
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'memory_percent': memory_percent,
                'memory_used_gb': memory_used,
                'memory_available_gb': memory_available,
                'disk_read_mb': disk_read,
                'disk_write_mb': disk_write,
                'network_sent_mb': net_sent,
                'network_recv_mb': net_recv,
                'phase': phase,
                'sample_id': sample_count
            }
            
            self.metrics.append(metric)
            sample_count += 1
            
            print(f"Sample {sample_count}: CPU={cpu_percent:.1f}%, Memory={memory_percent:.1f}%, Phase={phase}")
            time.sleep(interval)
        
        print(f"Collection complete. Collected {sample_count} samples.")
        return self.metrics
    
    def detect_phase(self, cpu_percent, memory_percent, io_rate):
        """
        Simple heuristic-based phase detection.
        
        Returns:
            Phase label: 'cpu_bound', 'io_bound', 'memory_bound', 'idle', or 'mixed'
        """
        # Thresholds
        cpu_threshold = 50.0
        memory_threshold = 70.0
        io_threshold = 10.0  # MB/s
        
        if cpu_percent < 10 and memory_percent < 30:
            return 'idle'
        elif cpu_percent > cpu_threshold and io_rate < io_threshold:
            return 'cpu_bound'
        elif io_rate > io_threshold and cpu_percent < cpu_threshold:
            return 'io_bound'
        elif memory_percent > memory_threshold:
            return 'memory_bound'
        else:
            return 'mixed'
    
    def save_to_csv(self, filepath=None):
        """Save collected metrics to CSV file."""
        if not self.metrics:
            print("No metrics to save.")
            return
        
        output_path = filepath or self.output_file
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        fieldnames = [
            'timestamp', 'cpu_percent', 'cpu_count',
            'memory_percent', 'memory_used_gb', 'memory_available_gb',
            'disk_read_mb', 'disk_write_mb',
            'network_sent_mb', 'network_recv_mb',
            'phase', 'sample_id'
        ]
        
        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.metrics)
        
        print(f"Metrics saved to {output_path}")
        print(f"Total samples: {len(self.metrics)}")
    
    def profile_process(self, process_path, duration=60, interval=1):
        """
        Profile a specific process.
        
        Args:
            process_path: Path to executable or script to profile
            duration: Profiling duration (seconds)
            interval: Sampling interval (seconds)
        """
        print(f"Profiling process: {process_path}")
        
        # Start the process
        try:
            self.process = subprocess.Popen(
                process_path,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except Exception as e:
            print(f"Error starting process: {e}")
            return
        
        # Collect metrics while process runs
        self.collect_metrics(duration, interval)
        
        # Cleanup
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(description='PhaseProfiler - System metrics profiler')
    parser.add_argument('program_path', nargs='?', help='Path to program to profile (optional)')
    parser.add_argument('--duration', type=int, default=60, help='Profiling duration in seconds (default: 60)')
    parser.add_argument('--interval', type=float, default=1.0, help='Sampling interval in seconds (default: 1.0)')
    parser.add_argument('--output', type=str, default='data/training_data.csv', help='Output CSV file path')
    
    args = parser.parse_args()
    
    profiler = PhaseProfiler(output_file=args.output)
    
    if args.program_path:
        profiler.profile_process(args.program_path, args.duration, args.interval)
    else:
        # Profile system-wide metrics
        profiler.collect_metrics(args.duration, args.interval)
    
    profiler.save_to_csv()
    print("Profiling complete!")


if __name__ == '__main__':
    main()

