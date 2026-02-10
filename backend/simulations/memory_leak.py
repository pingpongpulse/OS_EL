"""
Memory Leak Simulation
Simulates a memory leak where memory usage continuously grows without being freed
"""

import os
import sys
import time
import gc

def simulate_memory_leak(duration=60):
    """
    Simulate a memory leak by allocating memory without releasing it
    
    Args:
        duration: How long to run the simulation (seconds)
    """
    print(f"[Memory Leak] Starting {duration}s simulation...")
    start_time = time.time()
    
    # Global list to hold allocated memory (simulating memory leak)
    leaked_memory = []
    allocation_size = 1024 * 1024  # 1 MB chunks
    
    iteration = 0
    while time.time() - start_time < duration:
        iteration += 1
        
        # Allocate more memory without releasing it
        for i in range(10):
            # Create large object and don't release it
            large_object = [random_data for random_data in range(100000)]
            leaked_memory.append(large_object)
        
        # Also allocate some string data
        for i in range(100):
            large_string = "X" * (10 * 1024)  # 10 KB strings
            leaked_memory.append(large_string)
        
        elapsed = time.time() - start_time
        memory_allocated_mb = (len(leaked_memory) * allocation_size) / (1024 * 1024)
        
        if iteration % 5 == 0:
            print(f"[Memory Leak] Iteration {iteration} ({elapsed:.1f}s) - Allocated: ~{len(leaked_memory)} objects")
        
        # Small sleep to prevent instant completion
        time.sleep(0.1)
    
    # Don't clean up - that's the leak!
    print(f"[Memory Leak] Simulation finished - {len(leaked_memory)} objects still in memory")

def main():
    """Entry point for memory leak simulation"""
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    
    print(f"Memory Leak Simulation starting for {duration} seconds...")
    print("Expected behavior: CPU minimal (5-10%), memory grows continuously")
    print(f"PID: {os.getpid()}\n")
    
    try:
        # Disable garbage collection to prevent auto-cleanup
        gc.disable()
        
        print(f"Running memory leak simulation for {duration} seconds...")
        print("Expected: Rising memory usage, minimal CPU\n")
        
        simulate_memory_leak(duration)
        
        print(f"\n[Memory Leak] Simulation completed!")
        print("Note: Memory leak simulation shows continuous memory growth without release")
        
    except KeyboardInterrupt:
        print("\n[Memory Leak] Interrupted! Cleaning up...")
        gc.enable()
    except Exception as e:
        print(f"[Memory Leak] Error: {e}")
        gc.enable()

if __name__ == '__main__':
    main()
