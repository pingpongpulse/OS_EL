"""
Crypto Miner Simulation
Simulates a cryptographic mining process with high sustained CPU usage and steady memory consumption
"""

import os
import sys
import time
import multiprocessing
import hashlib
import random

def cpu_intensive_work(duration=60):
    """
    Perform CPU-intensive hashing operations to simulate crypto mining
    
    Args:
        duration: How long to run the simulation (seconds)
    """
    print(f"[Crypto Miner] Starting {duration}s simulation...")
    start_time = time.time()
    iteration = 0
    
    # Allocate memory for mining operations
    mining_data = {}
    
    while time.time() - start_time < duration:
        iteration += 1
        
        # Simulate mining: repeatedly hash random data
        for i in range(1000):
            random_data = os.urandom(64)
            hash_result = hashlib.sha256(random_data).hexdigest()
            
            # Store some results to simulate data collection
            if iteration % 100 == 0:
                mining_data[f"nonce_{iteration}_{i}"] = hash_result
        
        # Keep memory elevated
        if len(mining_data) > 10000:
            mining_data.clear()
            mining_data = {f"pool_{i}": hashlib.md5(str(i).encode()).hexdigest() 
                          for i in range(5000)}
        
        # Print progress
        if iteration % 10 == 0:
            elapsed = time.time() - start_time
            print(f"[Crypto Miner] Iteration {iteration} ({elapsed:.1f}s) - Memory pool: {len(mining_data)}")

def main():
    """Entry point for crypto miner simulation"""
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    
    print(f"Crypto Miner Simulation starting for {duration} seconds...")
    print("Expected behavior: High CPU usage (80-95%), steady memory growth")
    print(f"PID: {os.getpid()}\n")
    
    # Use multiprocessing to maximize CPU usage
    processes = []
    num_workers = multiprocessing.cpu_count()
    
    try:
        # Start workers
        for i in range(num_workers):
            p = multiprocessing.Process(target=cpu_intensive_work, args=(duration,))
            p.start()
            processes.append(p)
            print(f"[CPU Worker {i+1}] Started")
        
        print(f"\nRunning {num_workers} worker processes for {duration} seconds...")
        print("Expected: High sustained CPU, steady memory\n")
        
        # Wait for all workers
        for p in processes:
            p.join(timeout=duration + 5)
        
        print(f"\n[Crypto Miner] Simulation completed successfully!")
        
    except KeyboardInterrupt:
        print("\n[Crypto Miner] Interrupted! Cleaning up...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()
    except Exception as e:
        print(f"[Crypto Miner] Error: {e}")
        for p in processes:
            if p.is_alive():
                p.terminate()

if __name__ == '__main__':
    main()
