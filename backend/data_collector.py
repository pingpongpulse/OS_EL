"""
Data Collector Utility for PhaseSentinel.
Helps collect and merge data from multiple users for model training.
"""

import os
import csv
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional


class DataCollector:
    """Utility class for collecting and managing training data from multiple users."""
    
    def __init__(self, data_dir='data', api_url=None):
        """
        Initialize data collector.
        
        Args:
            data_dir: Directory to store data files
            api_url: API endpoint URL (if collecting via API)
        """
        self.data_dir = data_dir
        self.user_data_dir = os.path.join(data_dir, 'user_data')
        self.api_url = api_url or 'http://localhost:5000'
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.user_data_dir, exist_ok=True)
    
    def save_user_data(self, metrics: List[Dict], user_id: str, 
                      source: str = 'external', label: str = 'normal',
                      merge_to_training: bool = False):
        """
        Save metrics data from a user.
        
        Args:
            metrics: List of metric dictionaries
            user_id: Unique identifier for the user
            source: Source of data ('external', 'simulation', 'web')
            label: Label for the data ('normal', 'anomaly', etc.)
            merge_to_training: Whether to immediately merge into training_data.csv
            
        Returns:
            str: Path to saved file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        user_file = os.path.join(self.user_data_dir, f'{user_id}_{source}_{timestamp}.csv')
        
        if not metrics:
            raise ValueError("No metrics data provided")
        
        # Get fieldnames from first metric
        fieldnames = list(metrics[0].keys())
        # Add metadata columns
        for col in ['user_id', 'source', 'label', 'collection_timestamp']:
            if col not in fieldnames:
                fieldnames.append(col)
        
        # Write CSV
        with open(user_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for metric in metrics:
                row = dict(metric)
                row['user_id'] = user_id
                row['source'] = source
                row['label'] = label
                row['collection_timestamp'] = datetime.now().isoformat()
                writer.writerow(row)
        
        # Merge if requested
        if merge_to_training:
            self.merge_to_training(user_file)
        
        return user_file
    
    def merge_to_training(self, user_file: str):
        """Merge a user data file into main training_data.csv."""
        main_file = os.path.join(self.data_dir, 'training_data.csv')
        
        # Read user data
        user_metrics = []
        with open(user_file, 'r') as f:
            reader = csv.DictReader(f)
            user_metrics = list(reader)
        
        if not user_metrics:
            return
        
        # Get fieldnames
        fieldnames = list(user_metrics[0].keys())
        
        # Read existing training data
        existing_metrics = []
        if os.path.exists(main_file):
            with open(main_file, 'r') as f:
                reader = csv.DictReader(f)
                existing_metrics = list(reader)
                if existing_metrics:
                    existing_fieldnames = list(existing_metrics[0].keys())
                    fieldnames = list(set(fieldnames + existing_fieldnames))
        
        # Merge
        all_metrics = existing_metrics + user_metrics
        
        # Write merged data
        with open(main_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for metric in all_metrics:
                row = {field: metric.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        print(f"Merged {len(user_metrics)} samples from {user_file} into {main_file}")
    
    def merge_all_user_data(self):
        """Merge all user data files into training_data.csv."""
        import glob
        
        user_files = glob.glob(os.path.join(self.user_data_dir, '*.csv'))
        
        if not user_files:
            print("No user data files found")
            return 0
        
        merged_count = 0
        for user_file in user_files:
            try:
                self.merge_to_training(user_file)
                merged_count += 1
            except Exception as e:
                print(f"Error merging {user_file}: {e}")
        
        return merged_count
    
    def send_to_api(self, metrics: List[Dict], user_id: str,
                   source: str = 'external', label: str = 'normal',
                   merge_to_training: bool = False):
        """
        Send metrics data to API endpoint.
        
        Args:
            metrics: List of metric dictionaries
            user_id: User identifier
            source: Source of data
            label: Data label
            merge_to_training: Whether to merge into training data
            
        Returns:
            dict: API response
        """
        url = f"{self.api_url}/api/collect-data"
        payload = {
            'metrics': metrics,
            'user_id': user_id,
            'source': source,
            'label': label,
            'merge_to_training': merge_to_training
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error sending data to API: {e}")
            raise
    
    def get_stats(self):
        """Get statistics about collected data."""
        import glob
        
        stats = {
            'user_files': 0,
            'total_user_samples': 0,
            'users': {},
            'main_training_samples': 0
        }
        
        # Count user files
        user_files = glob.glob(os.path.join(self.user_data_dir, '*.csv'))
        stats['user_files'] = len(user_files)
        
        for user_file in user_files:
            try:
                with open(user_file, 'r') as f:
                    reader = csv.DictReader(f)
                    samples = list(reader)
                    stats['total_user_samples'] += len(samples)
                    
                    if samples:
                        user_id = samples[0].get('user_id', 'unknown')
                        if user_id not in stats['users']:
                            stats['users'][user_id] = 0
                        stats['users'][user_id] += len(samples)
            except Exception as e:
                print(f"Error reading {user_file}: {e}")
        
        # Count main training data
        main_file = os.path.join(self.data_dir, 'training_data.csv')
        if os.path.exists(main_file):
            with open(main_file, 'r') as f:
                reader = csv.DictReader(f)
                stats['main_training_samples'] = len(list(reader))
        
        return stats


# Example usage
if __name__ == '__main__':
    collector = DataCollector()
    
    # Example: Save data from a user
    sample_metrics = [
        {
            'timestamp': 0.0,
            'cpu_percent': 85.5,
            'memory_percent': 30.2,
            'memory_used_gb': 2.1,
            'disk_read_mb': 5.2,
            'disk_write_mb': 2.1,
            'network_sent_mb': 1.0,
            'network_recv_mb': 0.8,
            'phase': 'cpu_bound'
        }
    ]
    
    # Save locally
    file_path = collector.save_user_data(
        metrics=sample_metrics,
        user_id='user_001',
        source='external',
        label='normal',
        merge_to_training=True
    )
    print(f"Saved data to: {file_path}")
    
    # Get statistics
    stats = collector.get_stats()
    print(f"\nData Statistics:")
    print(f"  User files: {stats['user_files']}")
    print(f"  Total user samples: {stats['total_user_samples']}")
    print(f"  Main training samples: {stats['main_training_samples']}")
    print(f"  Users: {list(stats['users'].keys())}")


