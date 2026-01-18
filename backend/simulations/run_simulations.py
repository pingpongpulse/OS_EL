"""
Run Simulations for PhaseSentinel.
Runs each simulation script, collects metrics using phaseprofiler.py,
labels as anomaly, and saves to data/ directory.
"""

import os
import sys
import subprocess
import time
from datetime import datetime

# Add parent directory to path to import phaseprofiler
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phaseprofiler import PhaseProfiler


def run_simulation(simulation_name, script_path, duration=30, label='anomaly'):
    """
    Run a simulation script and collect metrics.
    
    Args:
        simulation_name: Name of the simulation (for output file)
        script_path: Path to simulation script
        duration: Duration to run simulation (seconds)
        label: Label for the collected data
        
    Returns:
        str: Path to saved CSV file
    """
    print(f"\n{'='*60}")
    print(f"Running simulation: {simulation_name}")
    print(f"{'='*60}")
    
    # Start simulation in background
    sim_process = subprocess.Popen(
        [sys.executable, script_path, str(duration)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Collect metrics while simulation runs
    # Use absolute path for data directory
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(backend_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    output_file = os.path.join(data_dir, f"{simulation_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    profiler = PhaseProfiler(output_file=output_file)
    
    print(f"Collecting metrics for {duration} seconds...")
    profiler.collect_metrics(duration=duration + 5, interval=0.5)  # Extra time for startup
    
    # Wait for simulation to complete
    try:
        sim_process.wait(timeout=duration + 10)
    except subprocess.TimeoutExpired:
        sim_process.terminate()
        sim_process.wait()
    
    # Save metrics
    profiler.save_to_csv()
    
    # Add label column if needed (for future ML training)
    # This would require modifying the CSV to add a 'label' column
    
    print(f"Metrics saved to: {output_file}")
    print(f"Total samples collected: {len(profiler.metrics)}")
    
    return output_file


def run_all_simulations():
    """Run all simulation scripts and collect labeled data."""
    print("="*60)
    print("PhaseSentinel Simulation Runner")
    print("="*60)
    
    # Get simulations directory
    sim_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(sim_dir)
    data_dir = os.path.join(backend_dir, 'data')
    
    # Ensure data directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    simulations = [
        {
            'name': 'miner',
            'script': os.path.join(sim_dir, 'miner_sim.py'),
            'duration': 30,
            'description': 'Crypto miner simulation (high CPU)'
        },
        {
            'name': 'leaky',
            'script': os.path.join(sim_dir, 'leaky.py'),
            'duration': 30,
            'description': 'Memory leak simulation'
        },
        {
            'name': 'fork_bomb',
            'script': os.path.join(sim_dir, 'fork_bomb.py'),
            'duration': 30,
            'description': 'Thread explosion simulation'
        }
    ]
    
    results = []
    
    for sim in simulations:
        if not os.path.exists(sim['script']):
            print(f"Warning: Simulation script not found: {sim['script']}")
            continue
        
        try:
            output_file = run_simulation(
                sim['name'],
                sim['script'],
                duration=sim['duration'],
                label='anomaly'
            )
            results.append({
                'simulation': sim['name'],
                'output_file': output_file,
                'status': 'success'
            })
            
            # Small delay between simulations
            print("\nWaiting 5 seconds before next simulation...")
            time.sleep(5)
            
        except Exception as e:
            print(f"Error running simulation {sim['name']}: {e}")
            results.append({
                'simulation': sim['name'],
                'status': 'error',
                'error': str(e)
            })
    
    # Summary
    print("\n" + "="*60)
    print("Simulation Summary")
    print("="*60)
    for result in results:
        status_icon = "✅" if result['status'] == 'success' else "❌"
        print(f"{status_icon} {result['simulation']}: {result['status']}")
        if 'output_file' in result:
            print(f"   Output: {result['output_file']}")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    
    # Merge all results into training_data.csv
    print("\nMerging results into training_data.csv...")
    merge_training_data(results, data_dir)
    
    print("\nAll simulations complete!")


def merge_training_data(results, data_dir):
    """Merge all simulation results into a single training_data.csv file."""
    import csv
    import glob
    
    # Find all CSV files from simulations
    csv_files = glob.glob(os.path.join(data_dir, '*.csv'))
    csv_files = [f for f in csv_files if 'training_data' not in f]
    
    if not csv_files:
        print("No simulation CSV files found to merge")
        return
    
    # Read and merge all CSV files
    all_metrics = []
    fieldnames = None
    
    for csv_file in csv_files:
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                if fieldnames is None:
                    fieldnames = reader.fieldnames
                
                for row in reader:
                    # Add label column
                    row['label'] = 'anomaly'
                    all_metrics.append(row)
            
            print(f"  Merged {csv_file}")
        except Exception as e:
            print(f"  Error reading {csv_file}: {e}")
    
    # Write merged data
    if all_metrics:
        output_file = os.path.join(data_dir, 'training_data.csv')
        if fieldnames:
            fieldnames = list(fieldnames) + ['label']
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_metrics)
        
        print(f"  Merged {len(all_metrics)} samples into {output_file}")


if __name__ == '__main__':
    run_all_simulations()


