"""
Memory Leak Simulation for PhaseSentinel.
Simulates growing memory usage (memory leak pattern) for testing anomaly detection.
"""

import time
import sys


def simulate_memory_leak(duration=30):
    """
    Simulate memory leak by continuously allocating memory.
    
    Args:
        duration: How long to run the simulation (seconds)
    """
    print(f"Starting memory leak simulation for {duration} seconds...")
    print("This will gradually consume memory.")
    
    memory_chunks = []
    start_time = time.time()
    allocation_count = 0
    
    try:
        while time.time() - start_time < duration:
            # Allocate memory (1MB chunks)
            chunk = bytearray(1024 * 1024)  # 1MB
            memory_chunks.append(chunk)
            allocation_count += 1
            
            # Keep some chunks to simulate leak (don't release all)
            if len(memory_chunks) > 100:
                # Only release every 10th chunk (simulating leak)
                if allocation_count % 10 != 0:
                    memory_chunks.pop(0)
            
            time.sleep(0.1)  # Small delay
            
            if allocation_count % 10 == 0:
                elapsed = time.time() - start_time
                memory_mb = len(memory_chunks)
                print(f"  Allocated {allocation_count} chunks, current memory: ~{memory_mb}MB, elapsed: {elapsed:.1f}s")
    
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
    except MemoryError:
        print("\nMemory limit reached - simulation stopped")
    
    # Cleanup
    memory_chunks.clear()
    print(f"\nMemory leak simulation complete. Total allocations: {allocation_count}")


if __name__ == '__main__':
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    simulate_memory_leak(duration)


