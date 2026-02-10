"""
CPU Intensive Simulation
Simulates a CPU-intensive workload with multiple threads competing for processing power
"""

import os
import sys
import time
import threading
import math

def cpu_workload_worker(worker_id, duration, shared_counter):
    """Worker function that performs CPU-intensive calculations"""
    start_time = time.time()
    iterations = 0
    
    print(f"[CPU Worker {worker_id}] Starting CPU-intensive work...")
    
    while time.time() - start_time < duration:
        # Perform CPU-intensive calculation (prime number checking)
        for i in range(1000):
            num = 1000000 + iterations * 1000 + i
            is_prime = True
            for j in range(2, int(math.sqrt(num)) + 1):
                if num % j == 0:
                    is_prime = False
                    break
            if is_prime:
                shared_counter[0] += 1
        
        iterations += 1
        
        # Small yield to prevent complete lockout of other threads
        time.sleep(0.001)
    
    print(f"[CPU Worker {worker_id}] Completed {iterations} iterations, found {shared_counter[0]} primes")


def simulate_cpu_intensive_work(duration=60, num_threads=4):
    """
    Simulate CPU-intensive work with multiple threads
    
    Args:
        duration: How long to run the simulation (seconds)
        num_threads: Number of CPU-intensive threads to create
    """
    print(f"[CPU Intensive] Starting {duration}s simulation with {num_threads} threads...")
    start_time = time.time()
    
    # Shared counter to create some contention
    shared_counter = [0]
    
    # Create worker threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(
            target=cpu_workload_worker, 
            args=(i, duration, shared_counter)
        )
        threads.append(thread)
        thread.start()
    
    # Monitor progress
    iteration = 0
    while time.time() - start_time < duration:
        iteration += 1
        elapsed = time.time() - start_time
        if iteration % 10 == 0:  # Print every 10 seconds approximately
            print(f"[CPU Monitor] {elapsed:.1f}s elapsed - Threads: {threading.active_count()}, Counter: {shared_counter[0]}")
        time.sleep(1)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join(timeout=duration + 5)
    
    elapsed = time.time() - start_time
    print(f"[CPU Intensive] Simulation finished after {elapsed:.1f}s - Total primes found: {shared_counter[0]}")


def main():
    """Entry point for CPU intensive simulation"""
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    num_threads = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    
    print(f"CPU Intensive Simulation starting for {duration} seconds with {num_threads} threads...")
    print("Expected behavior: High CPU usage (~100% for all cores), minimal memory/io usage")
    print(f"PID: {os.getpid()}\n")
    
    try:
        print(f"Running CPU intensive simulation for {duration} seconds...")
        print(f"Expected: {num_threads} threads competing for CPU resources\n")
        
        simulate_cpu_intensive_work(duration, num_threads)
        
        print(f"\n[CPU Intensive] Simulation completed!")
        print("Note: CPU intensive simulation creates multiple threads performing prime number calculations")
        
    except KeyboardInterrupt:
        print("\n[CPU Intensive] Interrupted! Cleaning up...")
    except Exception as e:
        print(f"[CPU Intensive] Error: {e}")


if __name__ == '__main__':
    main()