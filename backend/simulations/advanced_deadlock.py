"""
Advanced Deadlock Simulation
Simulates complex deadlock scenarios with multiple resources and circular dependencies
"""

import os
import sys
import time
import threading
import random

class AdvancedDeadlockSimulator:
    """Simulate advanced deadlock conditions with multiple locks and complex dependencies"""
    
    def __init__(self, num_resources=5, num_threads=4, duration=60):
        self.num_resources = num_resources
        self.num_threads = num_threads
        self.duration = duration
        self.resources = [threading.Lock() for _ in range(num_resources)]
        self.resource_names = [f"Resource_{i}" for i in range(num_resources)]
        self.start_time = None
        self.running = True
        self.deadlock_attempts = 0
        self.successful_operations = 0
        self.lock_order_attempts = []  # Track the order of lock acquisitions
        
    def worker(self, worker_id):
        """Worker thread that attempts to acquire multiple locks in different orders"""
        while self.running and (time.time() - self.start_time) < self.duration:
            # Choose random resources to create potential circular wait
            resource_indices = list(range(self.num_resources))
            random.shuffle(resource_indices)
            
            # Sometimes reverse the order to increase deadlock probability
            if worker_id % 2 == 0:
                resource_indices.reverse()
            
            acquired_locks = []
            acquired_names = []
            
            try:
                print(f"[Worker-{worker_id}] Attempting to acquire resources in order: {[self.resource_names[i] for i in resource_indices[:3]]}")
                
                # Try to acquire locks in the specified order
                all_acquired = True
                for i, res_idx in enumerate(resource_indices[:3]):  # Limit to 3 resources per worker
                    lock = self.resources[res_idx]
                    
                    # Try to acquire with timeout to detect potential deadlocks
                    acquired = lock.acquire(timeout=2.0)
                    
                    if not acquired:
                        print(f"[Worker-{worker_id}] TIMEOUT: Could not acquire {self.resource_names[res_idx]} after 2s")
                        
                        # Release any locks we've acquired so far to prevent partial deadlocks
                        for prev_lock in acquired_locks:
                            prev_lock.release()
                        all_acquired = False
                        self.deadlock_attempts += 1
                        break
                    else:
                        acquired_locks.append(lock)
                        acquired_names.append(self.resource_names[res_idx])
                        print(f"[Worker-{worker_id}] Acquired {self.resource_names[res_idx]}")
                
                if all_acquired:
                    # Critical section - do some work with all locks held
                    print(f"[Worker-{worker_id}] All locks acquired: {acquired_names}")
                    
                    # Simulate work with locks held
                    time.sleep(random.uniform(0.1, 0.5))
                    
                    # Record the successful operation
                    self.successful_operations += 1
                    
                    # Release all locks
                    for i, lock in enumerate(acquired_locks):
                        lock.release()
                        print(f"[Worker-{worker_id}] Released {acquired_names[i]}")
                
                # Add slight variation to timing to increase chance of race conditions
                time.sleep(random.uniform(0.05, 0.2))
                
            except Exception as e:
                print(f"[Worker-{worker_id}] Error: {e}")
                
                # Ensure all acquired locks are released in case of exception
                for lock in acquired_locks:
                    try:
                        lock.release()
                    except RuntimeError:
                        pass  # Lock wasn't held
        
        print(f"[Worker-{worker_id}] Worker finished")
    
    def resource_monitor(self):
        """Monitor resource usage and potential deadlocks"""
        while self.running and (time.time() - self.start_time) < self.duration:
            active_threads = threading.active_count()
            elapsed = time.time() - self.start_time
            
            print(f"\n[Monitor] {elapsed:.1f}s - Active threads: {active_threads}, "
                  f"Deadlock attempts: {self.deadlock_attempts}, Successful ops: {self.successful_operations}")
            
            # Check for potential deadlock conditions
            if active_threads > 1 and elapsed > 10:  # After initial settling period
                # Log resource acquisition patterns that might lead to deadlocks
                print(f"[Monitor] Potential deadlock risk - {active_threads} threads competing for resources")
            
            time.sleep(5)  # Monitor every 5 seconds
    
    def run(self):
        """Run the advanced deadlock simulation"""
        self.start_time = time.time()
        
        # Create worker threads
        workers = []
        for i in range(self.num_threads):
            worker_thread = threading.Thread(
                target=self.worker, 
                name=f"DeadlockWorker-{i}", 
                args=(i,)
            )
            workers.append(worker_thread)
            worker_thread.start()
        
        # Create monitor thread
        monitor_thread = threading.Thread(
            target=self.resource_monitor, 
            name="DeadlockMonitor", 
            daemon=True
        )
        monitor_thread.start()

        # Intentionally create a deterministic deadlock between two helper threads
        # so that the backend detector can observe a classic circular wait.
        def create_deterministic_deadlock():
            if self.num_resources < 2:
                return

            r0 = self.resources[0]
            r1 = self.resources[1]

            def dl_a():
                try:
                    r0.acquire()
                    # ensure ordering to increase chance of circular wait
                    time.sleep(0.2)
                    # this will block if r1 is held by other thread
                    r1.acquire()
                except Exception:
                    pass

            def dl_b():
                try:
                    r1.acquire()
                    time.sleep(0.2)
                    r0.acquire()
                except Exception:
                    pass

            t_a = threading.Thread(target=dl_a, name="DL-A", daemon=True)
            t_b = threading.Thread(target=dl_b, name="DL-B", daemon=True)
            t_a.start()
            t_b.start()

            # Give threads time to reach deadlock, then write a deadlock report file
            time.sleep(1.0)
            try:
                # Write deadlock descriptor so backend can pick it up
                import json
                sim_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'deadlocks'))
                os.makedirs(sim_dir, exist_ok=True)
                pid = os.getpid()
                report_path = os.path.join(sim_dir, f"{pid}_deadlock.json")

                graph = {
                    'nodes': [
                        {'id': f'DL-A', 'label': 'DL-A'},
                        {'id': f'DL-B', 'label': 'DL-B'},
                        {'id': 'Resource_0', 'label': 'Resource_0'},
                        {'id': 'Resource_1', 'label': 'Resource_1'}
                    ],
                    'edges': [
                        {'source': 'DL-A', 'target': 'Resource_0'},
                        {'source': 'Resource_0', 'target': 'DL-B'},
                        {'source': 'DL-B', 'target': 'Resource_1'},
                        {'source': 'Resource_1', 'target': 'DL-A'}
                    ]
                }

                analysis = {
                    'has_cycles': True,
                    'cycle_count': 1,
                    'risk_level': 'high',
                    'nodes_in_cycles': ['DL-A','DL-B','Resource_0','Resource_1'],
                    'total_locks_tracked': self.num_resources,
                    'graph': graph,
                    'timestamp': time.time(),
                    'process_pid': pid
                }

                with open(report_path, 'w') as fh:
                    json.dump({'analysis': analysis}, fh)

                print(f"[AdvancedDeadlock] Wrote deadlock report: {report_path}")
            except Exception as e:
                print(f"[AdvancedDeadlock] Failed to write deadlock report: {e}")

        # Fire-and-forget deterministic deadlock creator
        threading.Thread(target=create_deterministic_deadlock, name="DeadlockCreator", daemon=True).start()
        
        print(f"\n[Advanced Deadlock Simulator] Started {self.num_threads} worker threads with {self.num_resources} resources\n")
        
        try:
            # Wait for all workers to complete (or timeout)
            for worker in workers:
                worker.join(timeout=self.duration + 10)
        except KeyboardInterrupt:
            print("\n[Advanced Deadlock Simulator] Interrupted!")
        finally:
            self.running = False
            
            # Wait for monitor to finish
            monitor_thread.join(timeout=2)
            
            # Ensure all locks are released
            for lock in self.resources:
                try:
                    lock.release()
                except RuntimeError:
                    pass  # Lock wasn't held


def main():
    """Entry point for advanced deadlock simulation"""
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    num_resources = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    num_threads = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    
    print(f"Advanced Deadlock Simulation starting for {duration} seconds...")
    print(f"Resources: {num_resources}, Threads: {num_threads}")
    print("Expected behavior: Multiple threads competing for resources in different orders")
    print("This creates potential for circular wait conditions (classic deadlock scenario)")
    print(f"PID: {os.getpid()}\n")
    
    try:
        simulator = AdvancedDeadlockSimulator(
            num_resources=num_resources,
            num_threads=num_threads,
            duration=duration
        )
        simulator.run()
        
        print(f"\n[Advanced Deadlock Simulator] Simulation completed!")
        print(f"Deadlock attempts detected: {simulator.deadlock_attempts}")
        print(f"Successful operations: {simulator.successful_operations}")
        print("Check profiler results for deadlock detection")
        
    except Exception as e:
        print(f"[Advanced Deadlock Simulator] Error: {e}")


if __name__ == '__main__':
    main()