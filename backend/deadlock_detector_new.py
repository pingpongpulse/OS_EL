"""
DeadlockDetector - Detects potential deadlocks using wait-for graph analysis
Uses networkx to build wait-for graph and detect cycles (potential deadlocks)
"""

import threading
import networkx as nx
from collections import defaultdict
from datetime import datetime
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeadlockDetector:
    """Detects deadlock risks by analyzing lock wait-for graphs."""
    
    def __init__(self):
        self.locks = {}  # lock_id -> threading.Lock
        self.acquisitions = []  # List of lock acquisitions
        self.wait_graph = nx.DiGraph()
        self.lock_logs = []
        
    def create_lock(self, lock_id):
        """Create a new lock with given ID."""
        if lock_id not in self.locks:
            self.locks[lock_id] = threading.Lock()
        return self.locks[lock_id]
    
    def acquire_lock(self, thread_id, lock_id, timeout=5.0):
        """
        Simulate lock acquisition and log for deadlock analysis.
        
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
        
        log_entry = {
            'timestamp': timestamp,
            'thread_id': thread_id,
            'lock_id': lock_id,
            'action': 'acquire_attempt',
            'timeout': timeout
        }
        
        try:
            acquired = lock.acquire(timeout=timeout)
            log_entry['acquired'] = acquired
            if acquired:
                log_entry['action'] = 'acquired'
            else:
                log_entry['action'] = 'timeout'
                # Add wait edge in graph
                self._add_wait_edge(thread_id, lock_id)
            
            self.acquisitions.append(log_entry)
            self.lock_logs.append(log_entry)
            return acquired
            
        except Exception as e:
            log_entry['error'] = str(e)
            self.lock_logs.append(log_entry)
            return False
    
    def release_lock(self, thread_id, lock_id):
        """
        Release a lock and update wait-for graph.
        
        Args:
            thread_id: ID of thread releasing the lock
            lock_id: ID of lock to release
        """
        if lock_id in self.locks:
            try:
                self.locks[lock_id].release()
                timestamp = datetime.now().isoformat()
                log_entry = {
                    'timestamp': timestamp,
                    'thread_id': thread_id,
                    'lock_id': lock_id,
                    'action': 'release'
                }
                self.lock_logs.append(log_entry)
                # Remove wait edge if it exists
                self._remove_wait_edge(thread_id, lock_id)
            except Exception as e:
                logger.warning(f"Error releasing lock {lock_id}: {e}")
    
    def _add_wait_edge(self, thread_id, lock_id):
        """Add an edge indicating thread is waiting for lock."""
        self.wait_graph.add_edge(thread_id, lock_id)
    
    def _remove_wait_edge(self, thread_id, lock_id):
        """Remove a wait edge when lock is released."""
        if self.wait_graph.has_edge(thread_id, lock_id):
            self.wait_graph.remove_edge(thread_id, lock_id)
    
    def detect(self):
        """
        Detect potential deadlocks by finding cycles in the wait-for graph.
        
        Returns:
            dict: {risk: bool, cycles: list}
        """
        try:
            # Check for cycles in the wait-for graph
            cycles = list(nx.simple_cycles(self.wait_graph))
            
            has_deadlock_risk = len(cycles) > 0
            
            return {
                'risk': has_deadlock_risk,
                'cycles': cycles,
                'graph_size': self.wait_graph.number_of_nodes(),
                'edges': self.wait_graph.number_of_edges(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error detecting deadlock: {e}")
            return {
                'risk': False,
                'cycles': [],
                'error': str(e)
            }
    
    def analyze_deadlock_risk(self):
        """
        Comprehensive deadlock risk analysis.
        
        Returns:
            dict: Detailed analysis including risk level and recommendations
        """
        detection_result = self.detect()
        
        # Determine risk level
        if len(detection_result['cycles']) == 0:
            risk_level = 'low'
            recommendations = []
        elif len(detection_result['cycles']) <= 2:
            risk_level = 'medium'
            recommendations = [
                'Review lock ordering in critical sections',
                'Consider using timeouts on lock acquisitions'
            ]
        else:
            risk_level = 'high'
            recommendations = [
                'CRITICAL: Potential deadlock detected!',
                'Implement lock timeout mechanisms',
                'Use lock-free data structures where possible',
                'Review thread synchronization logic'
            ]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'risk_level': risk_level,
            'has_cycles': detection_result['risk'],
            'cycle_count': len(detection_result['cycles']),
            'cycles': detection_result['cycles'][:5],  # First 5 cycles
            'lock_count': len(self.locks),
            'acquisition_count': len(self.acquisitions),
            'recommendations': recommendations
        }
    
    def save_lock_logs(self, filepath='data/lock_logs.json'):
        """Save lock acquisition logs to JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.lock_logs, f, indent=2)
        logger.info(f"Lock logs saved to {filepath}")


# Backward compatibility alias
class LockTracker(DeadlockDetector):
    """Alias for backward compatibility."""
    pass

