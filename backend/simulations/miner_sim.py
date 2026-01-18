"""
Crypto Miner Simulation for PhaseSentinel.
Simulates high CPU usage (crypto mining pattern) for testing anomaly detection.
"""

import time
import sys


def simulate_mining(duration=30):
    """
    Simulate crypto mining by consuming CPU cycles.
    
    Args:
        duration: How long to run the simulation (seconds)
    """
    print(f"Starting crypto miner simulation for {duration} seconds...")
    print("This will consume high CPU resources.")
    
    start_time = time.time()
    iterations = 0
    
    try:
        while time.time() - start_time < duration:
            # CPU-intensive computation (simulating mining)
            result = 0
            for i in range(1000000):
                result += i * i % 1000
            
            iterations += 1
            if iterations % 10 == 0:
                elapsed = time.time() - start_time
                print(f"  Mining iteration {iterations}, elapsed: {elapsed:.1f}s")
    
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
    
    print(f"\nMining simulation complete. Total iterations: {iterations}")


if __name__ == '__main__':
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    simulate_mining(duration)


