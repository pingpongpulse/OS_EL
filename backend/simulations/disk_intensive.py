"""
Disk I/O Intensive Simulation
Simulates heavy disk read/write operations to create I/O bottlenecks
"""

import os
import sys
import time
import threading
import random
import tempfile

def disk_workload_worker(worker_id, duration, temp_dir):
    """Worker function that performs disk-intensive operations"""
    start_time = time.time()
    operations_count = 0
    
    print(f"[Disk Worker {worker_id}] Starting disk-intensive work in {temp_dir}...")
    
    while time.time() - start_time < duration:
        try:
            # Create a temporary file
            file_path = os.path.join(temp_dir, f"worker_{worker_id}_op_{operations_count}.tmp")
            
            # Write random data to file
            data_size = random.randint(1024*1024, 10*1024*1024)  # 1-10MB
            random_data = os.urandom(data_size)
            
            with open(file_path, 'wb') as f:
                f.write(random_data)
            
            # Read the file back
            with open(file_path, 'rb') as f:
                read_data = f.read()
            
            # Verify data integrity (optional)
            if read_data == random_data:
                operations_count += 1
            
            # Random delay to vary I/O patterns
            time.sleep(random.uniform(0.01, 0.1))
            
            # Clean up temp file occasionally to avoid filling disk
            if operations_count % 5 == 0:
                if os.path.exists(file_path):
                    os.remove(file_path)
            
        except Exception as e:
            print(f"[Disk Worker {worker_id}] Error: {e}")
            time.sleep(0.1)  # Brief pause on error
    
    print(f"[Disk Worker {worker_id}] Completed {operations_count} disk operations")


def simulate_disk_intensive_work(duration=60, num_threads=3):
    """
    Simulate disk-intensive work with multiple threads
    
    Args:
        duration: How long to run the simulation (seconds)
        num_threads: Number of disk-intensive threads to create
    """
    print(f"[Disk Intensive] Starting {duration}s simulation with {num_threads} threads...")
    start_time = time.time()
    
    # Create a temporary directory for this simulation
    temp_dir = tempfile.mkdtemp(prefix=f"disk_sim_{int(time.time())}_")
    print(f"[Disk Intensive] Using temp directory: {temp_dir}")
    
    # Create worker threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(
            target=disk_workload_worker, 
            args=(i, duration, temp_dir)
        )
        threads.append(thread)
        thread.start()
    
    # Monitor progress
    iteration = 0
    while time.time() - start_time < duration:
        iteration += 1
        elapsed = time.time() - start_time
        if iteration % 10 == 0:  # Print every 10 seconds approximately
            active_threads = threading.active_count()
            print(f"[Disk Monitor] {elapsed:.1f}s elapsed - Active threads: {active_threads}")
        time.sleep(1)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join(timeout=duration + 10)
    
    # Cleanup temp directory
    try:
        import shutil
        shutil.rmtree(temp_dir)
        print(f"[Disk Intensive] Cleaned up temp directory: {temp_dir}")
    except Exception as e:
        print(f"[Disk Intensive] Warning: Could not cleanup temp directory {temp_dir}: {e}")
    
    elapsed = time.time() - start_time
    print(f"[Disk Intensive] Simulation finished after {elapsed:.1f}s")


def main():
    """Entry point for disk intensive simulation"""
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    num_threads = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    
    print(f"Disk I/O Intensive Simulation starting for {duration} seconds with {num_threads} threads...")
    print("Expected behavior: High disk read/write activity, varying CPU usage")
    print(f"PID: {os.getpid()}\n")
    
    try:
        print(f"Running disk intensive simulation for {duration} seconds...")
        print(f"Expected: {num_threads} threads performing heavy disk I/O operations\n")
        
        simulate_disk_intensive_work(duration, num_threads)
        
        print(f"\n[Disk Intensive] Simulation completed!")
        print("Note: Disk intensive simulation creates multiple threads performing heavy read/write operations")
        
    except KeyboardInterrupt:
        print("\n[Disk Intensive] Interrupted! Cleaning up...")
    except Exception as e:
        print(f"[Disk Intensive] Error: {e}")


if __name__ == '__main__':
    main()