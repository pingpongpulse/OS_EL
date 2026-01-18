"""
Deadlock Risk Detector for PhaseSentinel.
Builds wait-for graph using networkx and detects cycles (potential deadlocks).
"""

import threading
import networkx as nx
from collections import defaultdict
from datetime import datetime
import json
import os


class LockTracker:
    """Tracks lock acquisitions and builds wait-for graph."""
    
    def __init__(self):
        self.locks = {}  # lock_id -> threading.Lock
        self.acquisitions = []  # List of (thread_id, lock_id, timestamp, acquired)
        self.wait_graph = nx.DiGraph()
        self.lock_logs = []
        
    def create_lock(self, lock_id):
        """Create a new lock with given ID."""
        if lock_id not in self.locks:
            self.locks[lock_id] = threading.Lock()
        return self.locks[lock_id]
    
    def acquire_lock(self, thread_id, lock_id, timeout=5.0):
        """
        Attempt to acquire a lock and log the attempt.
        
        Args:
            thread_id: ID of the thread attempting acquisition
            lock_id: ID of the lock to acquire
            timeout: Maximum time to wait for lock
            
        Returns:
            bool: True if acquired, False if timeout
        """
        if lock_id not in self.locks:
            self.create_lock(lock_id)
        
        lock = self.locks[lock_id]
        timestamp = datetime.now().isoformat()
        
        # Log acquisition attempt
        log_entry = {
            'thread_id': thread_id,
            'lock_id': lock_id,
            'timestamp': timestamp,
            'status': 'attempting'
        }
        self.lock_logs.append(log_entry)
        
        # Try to acquire lock
        acquired = lock.acquire(timeout=timeout)
        
        if acquired:
            log_entry['status'] = 'acquired'
            self.acquisitions.append((thread_id, lock_id, timestamp, True))
        else:
            log_entry['status'] = 'timeout'
            self.acquisitions.append((thread_id, lock_id, timestamp, False))
            # Add edge to wait-for graph: thread_id -> lock_id (waiting for)
            self.wait_graph.add_edge(thread_id, lock_id)
        
        return acquired
    
    def release_lock(self, thread_id, lock_id):
        """Release a lock."""
        if lock_id in self.locks:
            self.locks[lock_id].release()
            log_entry = {
                'thread_id': thread_id,
                'lock_id': lock_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'released'
            }
            self.lock_logs.append(log_entry)


class DeadlockDetector:
    """Detects deadlock risks by analyzing wait-for graph for cycles."""
    
    def __init__(self):
        self.tracker = LockTracker()
        self.detected_cycles = []
    
    def detect(self):
        """Flask-compatible detect() method for PhaseSentinel."""
        cycles = self.detect_cycles()
        return {
            'risk': len(cycles) > 0,
            'cycles': cycles,
            'cycle_count': len(cycles),
            'timestamp': datetime.now().isoformat()
        }
        
    def detect_cycles(self):
        """
        Detect cycles in the wait-for graph.
        Cycles indicate potential deadlocks.
        
        Returns:
            list: List of cycles found (each cycle is a list of nodes)
        """
        cycles = []
        
        try:
            # Find all simple cycles in the directed graph
            for cycle in nx.simple_cycles(self.tracker.wait_graph):
                cycles.append(cycle)
                self.detected_cycles.append({
                    'cycle': cycle,
                    'timestamp': datetime.now().isoformat(),
                    'risk_level': self._assess_risk(cycle)
                })
        except Exception as e:
            print(f"Error detecting cycles: {e}")
        
        return cycles
    
    def _assess_risk(self, cycle):
        """
        Assess the risk level of a detected cycle.
        
        Args:
            cycle: List of nodes forming a cycle
            
        Returns:
            str: Risk level ('high', 'medium', 'low')
        """
        if len(cycle) == 2:
            return 'high'  # Direct circular wait
        elif len(cycle) <= 4:
            return 'medium'
        else:
            return 'low'
    
    def analyze_deadlock_risk(self):
        """
        Comprehensive deadlock risk analysis.
        
        Returns:
            dict: Analysis results with detected cycles and recommendations
        """
        cycles = self.detect_cycles()
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_locks': len(self.tracker.locks),
            'total_acquisitions': len(self.tracker.acquisitions),
            'cycles_detected': len(cycles),
            'cycles': [
                {
                    'cycle': cycle,
                    'risk_level': self._assess_risk(cycle),
                    'description': self._describe_cycle(cycle)
                }
                for cycle in cycles
            ],
            'recommendations': self._generate_recommendations(cycles)
        }
        
        return analysis
    
    def _describe_cycle(self, cycle):
        """Generate human-readable description of a cycle."""
        if len(cycle) == 2:
            return f"Direct circular wait between {cycle[0]} and {cycle[1]}"
        else:
            return f"Circular wait involving {len(cycle)} entities: {' -> '.join(map(str, cycle))} -> {cycle[0]}"
    
    def _generate_recommendations(self, cycles):
        """Generate recommendations based on detected cycles."""
        recommendations = []
        
        if len(cycles) == 0:
            recommendations.append({
                'type': 'info',
                'message': 'No deadlock risks detected. Continue monitoring.'
            })
        else:
            recommendations.append({
                'type': 'warning',
                'message': f'{len(cycles)} potential deadlock(s) detected. Review lock acquisition order.'
            })
            
            # Specific recommendations
            if any(len(c) == 2 for c in cycles):
                recommendations.append({
                    'type': 'critical',
                    'message': 'Direct circular waits detected. Implement lock ordering or timeout mechanisms.'
                })
            
            recommendations.append({
                'type': 'suggestion',
                'message': 'Consider using lock timeouts, lock ordering, or deadlock detection algorithms.'
            })
        
        return recommendations
    
    def save_lock_logs(self, filepath='data/lock_logs.json'):
        """Save lock acquisition logs to JSON file."""
        output_dir = os.path.dirname(filepath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.tracker.lock_logs, f, indent=2)
        
        print(f"Lock logs saved to {filepath}")


def simulate_deadlock_scenario():
    """
    Simulate a deadlock scenario for testing.
    Creates two threads that acquire locks in different orders.
    """
    detector = DeadlockDetector()
    
    def thread_a():
        """Thread A: acquires lock1 then lock2"""
        thread_id = threading.current_thread().ident
        detector.tracker.acquire_lock(thread_id, 'lock1')
        threading.Event().wait(0.1)  # Simulate work
        detector.tracker.acquire_lock(thread_id, 'lock2')
        detector.tracker.release_lock(thread_id, 'lock2')
        detector.tracker.release_lock(thread_id, 'lock1')
    
    def thread_b():
        """Thread B: acquires lock2 then lock1 (opposite order = potential deadlock)"""
        thread_id = threading.current_thread().ident
        detector.tracker.acquire_lock(thread_id, 'lock2')
        threading.Event().wait(0.1)  # Simulate work
        detector.tracker.acquire_lock(thread_id, 'lock1')
        detector.tracker.release_lock(thread_id, 'lock1')
        detector.tracker.release_lock(thread_id, 'lock2')
    
    # Start threads
    t1 = threading.Thread(target=thread_a)
    t2 = threading.Thread(target=thread_b)
    
    t1.start()
    t2.start()
    
    t1.join(timeout=2)
    t2.join(timeout=2)
    
    # Analyze for deadlocks
    analysis = detector.analyze_deadlock_risk()
    detector.save_lock_logs()
    
    return analysis


if __name__ == '__main__':
    print("Testing deadlock detection...")
    analysis = simulate_deadlock_scenario()
    print(f"\nDeadlock Analysis:")
    print(f"Cycles detected: {analysis['cycles_detected']}")
    for cycle_info in analysis['cycles']:
        print(f"  - {cycle_info['description']} (Risk: {cycle_info['risk_level']})")


