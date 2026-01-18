"""
Flask server for PhaseSentinel web application.
Handles API endpoints, serves frontend templates, and orchestrates profiling,
deadlock detection, anomaly detection, and optimization recommendations.
"""

from flask import Flask, render_template, jsonify, request, send_file
import os
import json
import csv
from datetime import datetime
import subprocess
import sys

# Import PhaseSentinel modules
from phaseprofiler import PhasProfiler
from deadlock_detector import DeadlockDetector
from anomaly_detector import AnomalyDetector
from recommender import OptimizationRecommender

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'data')
MODELS_FOLDER = os.path.join(os.path.dirname(__file__), 'models')
ALLOWED_EXTENSIONS = {'py', 'txt', 'sh'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODELS_FOLDER, exist_ok=True)

# Initialize detectors and recommenders
anomaly_detector = AnomalyDetector()
recommender = OptimizationRecommender()


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Homepage - start profiling interface."""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Interactive dashboard showing metrics, phases, bottlenecks, anomalies, and deadlocks."""
    return render_template('dashboard.html')


@app.route('/results')
def results():
    """Results page showing recommendations and predicted impact."""
    return render_template('results.html')


@app.route('/api/profile', methods=['POST'])
def start_profiling():
    """Start profiling a program."""
    try:
        data = request.get_json()
        program_path = data.get('program_path')
        duration = data.get('duration', 60)  # Default 60 seconds
        
        if not program_path:
            return jsonify({'error': 'Program path is required'}), 400
        
        # Run the profiler
        profiler_script = os.path.join(os.path.dirname(__file__), 'phaseprofiler.py')
        result = subprocess.run(
            [sys.executable, profiler_script, program_path, '--duration', str(duration)],
            capture_output=True,
            text=True,
            timeout=duration + 30
        )
        
        if result.returncode != 0:
            return jsonify({
                'error': 'Profiling failed',
                'details': result.stderr
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Profiling completed',
            'output_file': 'training_data.csv'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get collected metrics data."""
    try:
        csv_file = os.path.join(UPLOAD_FOLDER, 'training_data.csv')
        
        if not os.path.exists(csv_file):
            return jsonify({'error': 'No metrics data found'}), 404
        
        # Read and parse CSV
        metrics = []
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                metrics.append(row)
        
        return jsonify({
            'status': 'success',
            'metrics': metrics,
            'count': len(metrics)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/phases', methods=['GET'])
def get_phases():
    """Get phase classification for metrics."""
    try:
        csv_file = os.path.join(UPLOAD_FOLDER, 'training_data.csv')
        
        if not os.path.exists(csv_file):
            return jsonify({'error': 'No metrics data found'}), 404
        
        # Read metrics and extract phases
        phases = []
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                phase_info = {
                    'timestamp': float(row.get('timestamp', 0)),
                    'phase': row.get('phase', 'unknown'),
                    'cpu_percent': float(row.get('cpu_percent', 0)),
                    'memory_percent': float(row.get('memory_percent', 0))
                }
                phases.append(phase_info)
        
        return jsonify({
            'status': 'success',
            'phases': phases
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/classify', methods=['POST'])
def classify_bottlenecks():
    """Classify bottlenecks using rule-based logic (no ML model required)."""
    try:
        data = request.get_json()
        metrics = data.get('metrics', [])
        
        if not metrics:
            # Try to get from CSV if no metrics provided
            csv_file = os.path.join(UPLOAD_FOLDER, 'training_data.csv')
            if os.path.exists(csv_file):
                with open(csv_file, 'r') as f:
                    reader = csv.DictReader(f)
                    metrics = list(reader)
        
        if not metrics:
            return jsonify({'error': 'No metrics provided'}), 400
        
        # Use rule-based classification from phaseprofiler
        profiler = PhasProfiler()
        classifications = []
        
        for metric in metrics:
            cpu = float(metric.get('cpu_percent', 0))
            memory = float(metric.get('memory_percent', 0))
            disk_read = float(metric.get('disk_read_mb', 0))
            disk_write = float(metric.get('disk_write_mb', 0))
            io_rate = disk_read + disk_write
            
            phase = profiler.detect_phase(cpu, memory, io_rate)
            classifications.append({
                'phase': phase,
                'cpu_percent': cpu,
                'memory_percent': memory,
                'io_rate': io_rate
            })
        
        return jsonify({
            'status': 'success',
            'classifications': classifications,
            'method': 'rule_based'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/deadlock', methods=['GET', 'POST'])
def detect_deadlock():
    """Detect deadlock risks."""
    try:
        detector = DeadlockDetector()
        
        # Run deadlock analysis
        analysis = detector.analyze_deadlock_risk()
        
        # Save lock logs
        detector.save_lock_logs()
        
        return jsonify({
            'status': 'success',
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/anomaly', methods=['POST'])
def detect_anomalies():
    """Detect security anomalies."""
    try:
        data = request.get_json()
        metrics = data.get('metrics', [])
        
        if not metrics:
            # Try to get from CSV if no metrics provided
            csv_file = os.path.join(UPLOAD_FOLDER, 'training_data.csv')
            if os.path.exists(csv_file):
                with open(csv_file, 'r') as f:
                    reader = csv.DictReader(f)
                    metrics = list(reader)
        
        if not metrics:
            return jsonify({'error': 'No metrics provided'}), 400
        
        # Use anomaly detector
        results = anomaly_detector.detect_anomalies(metrics)
        
        return jsonify({
            'status': 'success',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get optimization recommendations with predicted speedup."""
    try:
        data = request.get_json()
        metrics = data.get('metrics', [])
        phase_type = data.get('phase_type')
        
        if not metrics:
            # Try to get from CSV if no metrics provided
            csv_file = os.path.join(UPLOAD_FOLDER, 'training_data.csv')
            if os.path.exists(csv_file):
                with open(csv_file, 'r') as f:
                    reader = csv.DictReader(f)
                    metrics = list(reader)
        
        if not metrics:
            return jsonify({'error': 'No metrics provided'}), 400
        
        # Use recommender
        results = recommender.get_recommendations(metrics, phase_type)
        
        return jsonify({
            'status': 'success',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/predict-speedup', methods=['POST'])
def predict_speedup():
    """Predict optimization speedup using regression model."""
    try:
        data = request.get_json()
        metrics = data.get('metrics', [])
        
        if not metrics:
            return jsonify({'error': 'No metrics provided'}), 400
        
        # Use recommender to get speedup predictions
        results = recommender.get_recommendations(metrics)
        
        if 'error' in results:
            return jsonify({
                'status': 'error',
                'error': results['error'],
                'speedup': 1.0
            }), 500
        
        speedups = [r['predicted_speedup'] for r in results.get('recommendations', [])]
        
        return jsonify({
            'status': 'success',
            'speedup': speedups,
            'average_speedup': results.get('average_speedup', 1.0),
            'max_speedup': results.get('max_speedup', 1.0),
            'model_loaded': results.get('model_loaded', False)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/collect-data', methods=['POST'])
def collect_user_data():
    """
    Collect metrics data from multiple users for training.
    Accepts metrics data and saves it with user identifier.
    """
    try:
        data = request.get_json()
        metrics = data.get('metrics', [])
        user_id = data.get('user_id', 'anonymous')
        source = data.get('source', 'external')  # 'external', 'simulation', 'web'
        label = data.get('label', 'normal')  # 'normal', 'anomaly', etc.
        
        if not metrics or len(metrics) == 0:
            return jsonify({'error': 'No metrics data provided'}), 400
        
        # Create user-specific data directory
        user_data_dir = os.path.join(UPLOAD_FOLDER, 'user_data')
        os.makedirs(user_data_dir, exist_ok=True)
        
        # Save user-specific data file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        user_file = os.path.join(user_data_dir, f'{user_id}_{source}_{timestamp}.csv')
        
        # Write metrics to CSV
        if metrics:
            fieldnames = list(metrics[0].keys())
            # Add metadata columns if not present
            if 'user_id' not in fieldnames:
                fieldnames.append('user_id')
            if 'source' not in fieldnames:
                fieldnames.append('source')
            if 'label' not in fieldnames:
                fieldnames.append('label')
            if 'collection_timestamp' not in fieldnames:
                fieldnames.append('collection_timestamp')
            
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
        
        # Optionally merge into main training_data.csv
        merge_to_training = data.get('merge_to_training', False)
        if merge_to_training:
            merge_user_data_to_training(user_file)
        
        return jsonify({
            'status': 'success',
            'message': f'Data collected from user {user_id}',
            'samples': len(metrics),
            'file': user_file,
            'merged': merge_to_training
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def merge_user_data_to_training(user_file):
    """Merge user-specific data file into main training_data.csv."""
    try:
        main_file = os.path.join(UPLOAD_FOLDER, 'training_data.csv')
        
        # Read user data
        user_metrics = []
        with open(user_file, 'r') as f:
            reader = csv.DictReader(f)
            user_metrics = list(reader)
        
        if not user_metrics:
            return
        
        # Read existing training data if it exists
        existing_metrics = []
        fieldnames = list(user_metrics[0].keys())
        
        if os.path.exists(main_file):
            with open(main_file, 'r') as f:
                reader = csv.DictReader(f)
                existing_metrics = list(reader)
                # Ensure fieldnames match
                if existing_metrics:
                    existing_fieldnames = list(existing_metrics[0].keys())
                    fieldnames = list(set(fieldnames + existing_fieldnames))
        
        # Merge data
        all_metrics = existing_metrics + user_metrics
        
        # Write merged data
        with open(main_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for metric in all_metrics:
                # Ensure all fields are present
                row = {field: metric.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        print(f"Merged {len(user_metrics)} samples from {user_file} into {main_file}")
        
    except Exception as e:
        print(f"Error merging user data: {e}")


@app.route('/api/merge-all-data', methods=['POST'])
def merge_all_user_data():
    """
    Merge all user-specific data files into training_data.csv.
    Useful for consolidating data from multiple users before training.
    """
    try:
        user_data_dir = os.path.join(UPLOAD_FOLDER, 'user_data')
        
        if not os.path.exists(user_data_dir):
            return jsonify({
                'status': 'success',
                'message': 'No user data directory found',
                'merged_files': 0
            })
        
        # Find all user data CSV files
        import glob
        user_files = glob.glob(os.path.join(user_data_dir, '*.csv'))
        
        if not user_files:
            return jsonify({
                'status': 'success',
                'message': 'No user data files found',
                'merged_files': 0
            })
        
        merged_count = 0
        for user_file in user_files:
            try:
                merge_user_data_to_training(user_file)
                merged_count += 1
            except Exception as e:
                print(f"Error merging {user_file}: {e}")
        
        # Get final count
        main_file = os.path.join(UPLOAD_FOLDER, 'training_data.csv')
        total_samples = 0
        if os.path.exists(main_file):
            with open(main_file, 'r') as f:
                reader = csv.DictReader(f)
                total_samples = len(list(reader))
        
        return jsonify({
            'status': 'success',
            'message': f'Merged {merged_count} user data files',
            'merged_files': merged_count,
            'total_samples': total_samples
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user-data-stats', methods=['GET'])
def get_user_data_stats():
    """Get statistics about collected user data."""
    try:
        user_data_dir = os.path.join(UPLOAD_FOLDER, 'user_data')
        main_file = os.path.join(UPLOAD_FOLDER, 'training_data.csv')
        
        stats = {
            'user_files': 0,
            'total_user_samples': 0,
            'users': {},
            'main_training_samples': 0
        }
        
        # Count user files
        if os.path.exists(user_data_dir):
            import glob
            user_files = glob.glob(os.path.join(user_data_dir, '*.csv'))
            stats['user_files'] = len(user_files)
            
            # Count samples per user
            for user_file in user_files:
                try:
                    with open(user_file, 'r') as f:
                        reader = csv.DictReader(f)
                        samples = list(reader)
                        stats['total_user_samples'] += len(samples)
                        
                        # Count by user_id
                        if samples:
                            user_id = samples[0].get('user_id', 'unknown')
                            if user_id not in stats['users']:
                                stats['users'][user_id] = 0
                            stats['users'][user_id] += len(samples)
                except Exception as e:
                    print(f"Error reading {user_file}: {e}")
        
        # Count main training data
        if os.path.exists(main_file):
            with open(main_file, 'r') as f:
                reader = csv.DictReader(f)
                stats['main_training_samples'] = len(list(reader))
        
        return jsonify({
            'status': 'success',
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'models_available': {
            'anomaly': os.path.exists(os.path.join(MODELS_FOLDER, 'anomaly_model.pkl')),
            'regression': os.path.exists(os.path.join(MODELS_FOLDER, 'regression_model.pkl'))
        },
        'detectors': {
            'anomaly_loaded': anomaly_detector.model_loaded,
            'recommender_loaded': recommender.model_loaded
        }
    })


if __name__ == '__main__':
    print("Starting PhaseSentinel Flask server...")
    print(f"Templates folder: {app.template_folder}")
    print(f"Static folder: {app.static_folder}")
    print(f"Models folder: {MODELS_FOLDER}")
    print(f"Data folder: {UPLOAD_FOLDER}")
    app.run(debug=True, host='0.0.0.0', port=5000)
