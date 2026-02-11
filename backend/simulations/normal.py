#!/usr/bin/env python3
"""
Normal.py - A generic program demonstrating normal system behavior.
Performs legitimate operations with balanced resource usage.
Does not trigger anomaly detection.
"""

import time
import math
import random
import sys

def simple_calculation():
    """Perform simple mathematical calculations."""
    result = 0
    for i in range(1000):
        result += math.sqrt(i) * math.sin(i)
    return result

def process_data():
    """Process data in a normal manner."""
    data = list(range(1000))
    processed = [x * 2 for x in data]
    return sum(processed)

def simulate_io_operation():
    """Simulate normal I/O operation."""
    try:
        # Read a file from the system
        with open('/etc/hostname', 'r') as f:
            hostname = f.read().strip()
        return hostname
    except:
        # Fallback if not on Unix-like system
        return "System"

def string_operations():
    """Perform normal string operations."""
    text = "The quick brown fox jumps over the lazy dog"
    words = text.split()
    uppercase = [word.upper() for word in words]
    return ' '.join(uppercase)

def matrix_operations():
    """Perform normal matrix-like operations."""
    matrix = [[random.random() for _ in range(10)] for _ in range(10)]
    
    # Calculate row sums
    row_sums = [sum(row) for row in matrix]
    
    # Calculate column sums
    col_sums = [sum(matrix[i][j] for i in range(len(matrix))) 
                for j in range(len(matrix[0]))]
    
    return row_sums, col_sums

def dictionary_operations():
    """Perform normal dictionary operations."""
    data = {
        'name': 'System Monitor',
        'version': '1.0',
        'status': 'normal',
        'threads': 4,
        'operations': 0
    }
    
    # Simulate updates
    data['operations'] += 1
    data['last_update'] = time.time()
    
    return data

def list_operations():
    """Perform normal list operations."""
    numbers = list(range(100))
    
    # Normal operations
    numbers.append(100)
    numbers.extend([101, 102, 103])
    numbers.sort()
    
    # Calculate statistics
    avg = sum(numbers) / len(numbers)
    
    return avg

def sleep_operation():
    """Normal sleep operation to simulate realistic behavior."""
    time.sleep(0.1)

def main():
    """Main function - performs normal operations in balanced manner."""
    print("Starting Normal Program...")
    print("=" * 50)
    
    operations = 0
    start_time = time.time()
    
    try:
        # Run for a reasonable duration (5-10 seconds)
        while time.time() - start_time < 10:
            
            # Perform various normal operations
            if operations % 5 == 0:
                result = simple_calculation()
                print(f"[{operations}] Calculation: {result:.2f}")
            
            if operations % 5 == 1:
                data_sum = process_data()
                print(f"[{operations}] Data Processing: {data_sum}")
            
            if operations % 5 == 2:
                matrix_data = matrix_operations()
                print(f"[{operations}] Matrix Operations: {len(matrix_data[0])} rows, {len(matrix_data[1])} cols")
            
            if operations % 5 == 3:
                dict_data = dictionary_operations()
                print(f"[{operations}] Dictionary Update: {dict_data['operations']} ops")
            
            if operations % 5 == 4:
                list_avg = list_operations()
                print(f"[{operations}] List Operations: avg={list_avg:.2f}")
            
            # Perform string operations occasionally
            if operations % 3 == 0:
                text_result = string_operations()
            
            # Perform I/O occasionally
            if operations % 7 == 0:
                io_result = simulate_io_operation()
            
            # Small sleep to avoid consuming all CPU (normal behavior)
            sleep_operation()
            
            operations += 1
        
        print("=" * 50)
        print(f"Program completed successfully")
        print(f"Total operations: {operations}")
        print(f"Duration: {time.time() - start_time:.2f} seconds")
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        print(f"Completed {operations} operations")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
