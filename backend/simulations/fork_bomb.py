"""
Fork Bomb / Thread Explosion Simulation for PhaseSentinel.
Spawns many threads to simulate thread explosion pattern for testing deadlock detection.
"""

import threading
import time
import sys


def worker_thread(thread_id, duration):
    """
    Worker thread that does some work and uses locks.
    
    Args:
        thread_id: Unique thread identifier
        duration: How long the thread should run (seconds)
    """
    start_time = time.time()
    iterations = 0
    
    # Simulate some work
    while time.time() - start_time < duration:
        # Do some computation
        result = sum(i * i for i in range(1000))
        iterations += 1
        time.sleep(0.01)  # Small sleep to prevent complete CPU lock
    
    # print(f"Thread {thread_id} completed {iterations} iterations")


def simulate_thread_explosion(num_threads=50, duration=30):
    """
    Simulate thread explosion by spawning many threads.
    
    Args:
        num_threads: Number of threads to spawn
        duration: How long threads should run (seconds)
    """
    print(f"Starting thread explosion simulation...")
    print(f"Spawning {num_threads} threads for {duration} seconds...")
    
    threads = []
    start_time = time.time()
    
    try:
        # Spawn threads
        for i in range(num_threads):
            thread = threading.Thread(
                target=worker_thread,
                args=(i, duration),
                name=f"Worker-{i}"
            )
            thread.start()
            threads.append(thread)
            
            if (i + 1) % 10 == 0:
                print(f"  Spawned {i + 1}/{num_threads} threads...")
        
        print(f"\nAll {num_threads} threads spawned. Waiting for completion...")
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=duration + 5)
        
        elapsed = time.time() - start_time
        print(f"\nThread explosion simulation complete. Elapsed: {elapsed:.1f}s")
        
    except Exception as e:
        print(f"\nError during simulation: {e}")
    finally:
        # Cleanup - ensure all threads are terminated
        for thread in threads:
            if thread.is_alive():
                print(f"Warning: Thread {thread.name} is still alive")


if __name__ == '__main__':
    num_threads = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    simulate_thread_explosion(num_threads, duration)


