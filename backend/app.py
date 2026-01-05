"""
Flask server for PhaseProfiler web application.
Handles API endpoints, serves frontend templates, and orchestrates profiling.
"""

from flask import Flask, render_template, jsonify, request, send_file
import os
import json
from datetime import datetime
import subprocess
import sys

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


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Homepage - start profiling interface."""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Interactive dashboard showing metrics, phases, and bottlenecks."""
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
            [sys.executable, profiler_script, program_path, str(duration)],
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
            lines = f.readlines()
            if len(lines) > 1:
                headers = lines[0].strip().split(',')
                for line in lines[1:]:
                    values = line.strip().split(',')
                    if len(values) == len(headers):
                        metrics.append(dict(zip(headers, values)))
        
        return jsonify({
            'status': 'success',
            'metrics': metrics,
            'count': len(metrics)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/classify', methods=['POST'])
def classify_bottlenecks():
    """Classify bottlenecks using trained ML model."""
    try:
        import pickle
        
        model_file = os.path.join(MODELS_FOLDER, 'bottleneck_classifier.pkl')
        
        if not os.path.exists(model_file):
            return jsonify({
                'error': 'Model not found. Please train the model first.',
                'classifications': []
            }), 404
        
        # Load model
        with open(model_file, 'rb') as f:
            model = pickle.load(f)
        
        data = request.get_json()
        features = data.get('features', [])
        
        if not features:
            return jsonify({'error': 'Features are required'}), 400
        
        # Classify bottlenecks
        predictions = model.predict(features)
        probabilities = model.predict_proba(features) if hasattr(model, 'predict_proba') else None
        
        return jsonify({
            'status': 'success',
            'predictions': predictions.tolist(),
            'probabilities': probabilities.tolist() if probabilities is not None else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/predict-speedup', methods=['POST'])
def predict_speedup():
    """Predict optimization speedup using regression model."""
    try:
        import pickle
        
        model_file = os.path.join(MODELS_FOLDER, 'regression_model.pkl')
        
        if not os.path.exists(model_file):
            return jsonify({
                'error': 'Regression model not found. Please train the model first.',
                'speedup': 1.0
            }), 404
        
        # Load model
        with open(model_file, 'rb') as f:
            model = pickle.load(f)
        
        data = request.get_json()
        features = data.get('features', [])
        
        if not features:
            return jsonify({'error': 'Features are required'}), 400
        
        # Predict speedup
        predictions = model.predict(features)
        
        return jsonify({
            'status': 'success',
            'speedup': predictions.tolist(),
            'predicted_improvement': f"{(predictions[0] - 1) * 100:.1f}%" if len(predictions) > 0 else "N/A"
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
            'classifier': os.path.exists(os.path.join(MODELS_FOLDER, 'bottleneck_classifier.pkl')),
            'regression': os.path.exists(os.path.join(MODELS_FOLDER, 'regression_model.pkl'))
        }
    })


if __name__ == '__main__':
    print("Starting PhaseProfiler Flask server...")
    print(f"Templates folder: {app.template_folder}")
    print(f"Static folder: {app.static_folder}")
    app.run(debug=True, host='0.0.0.0', port=5000)

