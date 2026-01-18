"""
Phase Profiler for PhaseSentinel.
Collects metrics (CPU, I/O, memory), detects phases using rule-based logic,
and classifies bottlenecks (cpu_bound, io_bound, memory_bound, idle, mixed).
"""

import psutil
import time
import csv
import sys
import os
import subprocess
from datetime import datetime
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PhasProfiler:
    """Profiles system metrics and detects execution phases."""
    
    def __init__(self, output_file='training_data.csv', sample_interval=0.5):
        self.output_file = output_file
        self.metrics = []
        self.phases = []
        self.sample_interval = sample_interval
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
        return {
            'phases': self._segment_phases(),
            'timeline': self.metrics,
            'summary': self._generate_summary(),
            'metrics': self.metrics
        }
    
    def profile(self, duration=10, pid=None):
        """Flask-compatible profile() method."""
        return self.collect_metrics(duration=duration, interval=self.sample_interval)
    
    def _segment_phases(self):
        """Segment metrics into continuous phases of the same type."""
        if not self.metrics:
            return []
        phases = []
        current_phase = {
            'start': self.metrics[0]['timestamp'],
            'type': self.metrics[0]['phase'],
            'metrics': [self.metrics[0]]
        }
        for metric in self.metrics[1:]:
            if metric['phase'] == current_phase['type']:
                current_phase['metrics'].append(metric)
            else:
                current_phase['end'] = current_phase['metrics'][-1]['timestamp']
                current_phase['duration'] = current_phase['end'] - current_phase['start']
                cpus = [m['cpu_percent'] for m in current_phase['metrics']]
                current_phase['avg_cpu'] = sum(cpus) / len(cpus)
                current_phase['max_cpu'] = max(cpus)
                phases.append(current_phase)
                current_phase = {
                    'start': metric['timestamp'],
                    'type': metric['phase'],
                    'metrics': [metric]
                }
        if current_phase['metrics']:
            current_phase['end'] = current_phase['metrics'][-1]['timestamp']
            current_phase['duration'] = current_phase['end'] - current_phase['start']
            cpus = [m['cpu_percent'] for m in current_phase['metrics']]
            current_phase['avg_cpu'] = sum(cpus) / len(cpus)
            current_phase['max_cpu'] = max(cpus)
            phases.append(current_phase)
        return phases
    
    def _generate_summary(self):
        """Generate summary statistics."""
        if not self.metrics:
            return {}
        cpus = [m['cpu_percent'] for m in self.metrics]
        mems = [m['memory_percent'] for m in self.metrics]
        return {
            'avg_cpu': sum(cpus) / len(cpus),
            'max_cpu': max(cpus),
            'avg_memory_percent': sum(mems) / len(mems),
            'max_memory_percent': max(mems),
            'total_samples': len(self.metrics)
        }
    
    def detect_phase(self, cpu_percent, memory_percent, io_rate):
        """
        Rule-based phase detection and bottleneck classification.
        
        Args:
            cpu_percent: CPU usage percentage
            memory_percent: Memory usage percentage
            io_rate: I/O rate in MB/s
            
        Returns:
            Phase label: 'cpu_bound', 'io_bound', 'memory_bound', 'idle', or 'mixed'
        """
        # Thresholds for phase detection
        cpu_threshold = 70.0  # CPU > 70% indicates CPU-bound
        memory_threshold = 70.0  # Memory > 70% indicates memory-bound
        io_threshold = 10.0  # I/O > 10 MB/s indicates I/O-bound
        idle_cpu_threshold = 10.0
        idle_memory_threshold = 30.0
        
        # Rule-based classification
        if cpu_percent < idle_cpu_threshold and memory_percent < idle_memory_threshold:
            return 'idle'
        elif cpu_percent > cpu_threshold and io_rate < io_threshold and memory_percent < memory_threshold:
            return 'cpu_bound'
        elif io_rate > io_threshold and cpu_percent < cpu_threshold:
            return 'io_bound'
        elif memory_percent > memory_threshold and cpu_percent < cpu_threshold:
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

