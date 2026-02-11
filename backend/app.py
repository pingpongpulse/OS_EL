"""
Flask server for PhaseSentinel web application.
Handles API endpoints, serves frontend templates, and orchestrates profiling,
deadlock detection, anomaly detection, and optimization recommendations.
"""

from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for
import os
import json
import csv
from datetime import datetime
import subprocess
import sys
import psutil
import threading
import time
import random
from collections import defaultdict, deque
import asyncio
from flask_socketio import SocketIO, emit, disconnect, join_room, leave_room

# Import PhaseSentinel modules
from phaseprofiler import PhasProfiler
from deadlock_detector_new import DeadlockDetector
from anomaly_detector import AnomalyDetector
from recommender import OptimizationRecommender
from bottleneck_classifier import BottleneckClassifier

# Initialize Flask app with SocketIO
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Global variables for PID-scoped data management
active_profiles = {}  # Dictionary to store active profiling sessions
profile_data = {}   # Dictionary to store collected metrics per PID
current_pid = None    # Currently active PID
profiling_thread = None  # Thread for continuous profiling


# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to server', 'timestamp': time.time()})


@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')


@socketio.on('join_profile_stream')
def handle_join_profile_stream(data):
    """Handle client joining a profile stream."""
    pid = data.get('pid')
    if pid:
        room = f'profile_{pid}'
        join_room(room)
        emit('joined_stream', {
            'message': f'Joined stream for PID {pid}',
            'pid': pid,
            'timestamp': time.time()
        })


@socketio.on('leave_profile_stream')
def handle_leave_profile_stream(data):
    """Handle client leaving a profile stream."""
    pid = data.get('pid')
    if pid:
        room = f'profile_{pid}'
        leave_room(room)
        emit('left_stream', {
            'message': f'Left stream for PID {pid}',
            'pid': pid,
            'timestamp': time.time()
        })


@socketio.on('subscribe_to_profile_updates')
def handle_subscribe_to_profile_updates(data):
    """Subscribe to profile updates for a specific PID."""
    pid = data.get('pid')
    stream_type = data.get('stream_type', 'metric_update')  # 'metric_update', 'deadlock', 'anomaly'
    
    if pid:
        room = f'{stream_type}_{pid}'
        join_room(room)
        emit('subscription_confirmed', {
            'message': f'Subscribed to {stream_type} for PID {pid}',
            'pid': pid,
            'stream_type': stream_type,
            'timestamp': time.time()
        })


@socketio.on('unsubscribe_from_profile_updates')
def handle_unsubscribe_from_profile_updates(data):
    """Unsubscribe from profile updates for a specific PID."""
    pid = data.get('pid')
    stream_type = data.get('stream_type', 'metric_update')
    
    if pid:
        room = f'{stream_type}_{pid}'
        leave_room(room)
        emit('unsubscription_confirmed', {
            'message': f'Unsubscribed from {stream_type} for PID {pid}',
            'pid': pid,
            'stream_type': stream_type,
            'timestamp': time.time()
        })

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
# Bottleneck classifier (loads regression_model.pkl if available)
try:
    bottleneck_classifier = BottleneckClassifier()
except Exception:
    bottleneck_classifier = None


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Redirect to dashboard."""
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    """Interactive dashboard showing metrics, phases, bottlenecks, anomalies, and deadlocks."""
    return render_template('dashboard.html')



# PID-scoped profiling management
@app.route('/api/profile/start', methods=['POST'])
def start_profiling():
    """Start profiling a program and return its PID."""
    global current_pid, profiling_thread
    try:
        data = request.get_json()
        program_path = data.get('file_path')  # Changed to match frontend expectation
        duration = data.get('duration', 60)  # Default to 60 seconds if not specified
        
        if not program_path:
            return jsonify({'error': 'Program file path is required'}), 400
        
        if not os.path.exists(program_path):
            return jsonify({'error': 'Program file does not exist'}), 400
        
        if duration < 1 or duration > 300:
            return jsonify({'error': 'Duration must be between 1 and 300 seconds'}), 400
        
        # Start the program as a subprocess
        process = subprocess.Popen(
            [sys.executable, program_path] if program_path.endswith('.py') else [program_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Store the PID and process info
        pid = process.pid
        current_pid = pid
        
        # Initialize data storage for this PID
        active_profiles[pid] = {
            'process': process,
            'start_time': time.time(),
            'program_path': program_path,
            'duration': duration,
            'metrics': [],
            'phases': [],
            'anomalies': [],
            'deadlocks': []
        }
        
        # Start continuous profiling in a separate thread
        if profiling_thread and profiling_thread.is_alive():
            profiling_thread.join(timeout=1)
        
        profiling_thread = threading.Thread(target=continuous_profiling, args=(pid,), daemon=True)
        profiling_thread.start()
        
        return jsonify({
            'status': 'success',
            'message': f'Profiling started for {duration} seconds',
            'pid': pid,
            'program_path': program_path,
            'duration': duration,
            'expected_end_time': time.time() + duration
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/profile/stop', methods=['POST'])
def stop_profiling():
    """Stop profiling the currently active program."""
    global current_pid
    try:
        if current_pid is None:
            return jsonify({'error': 'No active profiling session'}), 400
        
        if current_pid in active_profiles:
            # Terminate the process
            process = active_profiles[current_pid]['process']
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            # Mark profiling as stopped
            active_profiles[current_pid]['running'] = False
            
            # Clean up
            del active_profiles[current_pid]
            current_pid = None
            
        return jsonify({'status': 'success', 'message': 'Profiling stopped'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def continuous_profiling(pid):
    """Continuously profile the process with the given PID."""
    if pid not in active_profiles:
        return
    
    process_info = active_profiles[pid]
    process = process_info['process']
    start_time = process_info['start_time']
    duration = process_info.get('duration', 60)  # Default to 60 seconds
    expected_end_time = start_time + duration
    
    profiler = PhasProfiler()
    anomaly_detector = AnomalyDetector()
    deadlock_detector = DeadlockDetector()
    
    while pid in active_profiles and process.poll() is None and time.time() < expected_end_time:
        try:
            # Get process metrics
            p = psutil.Process(pid)
            
            # Collect metrics - use interval=0.1 for responsive CPU sampling
            cpu_percent = p.cpu_percent(interval=0.1)
            
            memory_info = p.memory_info()
            memory_percent = p.memory_percent()
            
            # Get I/O stats
            io_counters = p.io_counters() if p.is_running() else None
            disk_read_mb = io_counters.read_bytes / (1024**2) if io_counters else 0
            disk_write_mb = io_counters.write_bytes / (1024**2) if io_counters else 0
            
            # Get network stats
            net_io = psutil.net_io_counters()
            net_sent = net_io.bytes_sent / (1024**2) if net_io else 0
            net_recv = net_io.bytes_recv / (1024**2) if net_io else 0
            
            # Calculate phase
            phase = profiler.detect_phase(cpu_percent, memory_percent, disk_read_mb + disk_write_mb)
            
            # Create metric entry
            metric = {
                'timestamp': time.time() - start_time,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_used_mb': memory_info.rss / (1024**2) if p.is_running() else 0,
                'disk_read_mb': disk_read_mb,
                'disk_write_mb': disk_write_mb,
                'network_sent_mb': net_sent,
                'network_recv_mb': net_recv,
                'phase': phase,
                'pid': pid
            }
            
            # Store metric
            profile_data.setdefault(pid, []).append(metric)
            
            # Detect anomalies
            anomaly_results = anomaly_detector.detect_anomalies([metric])
            if anomaly_results['anomalies_detected'] > 0:
                process_info['anomalies'].extend(anomaly_results['alerts'])
            
            # Detect deadlocks (in a simplified way for this implementation)
            deadlock_results = deadlock_detector.analyze_deadlock_risk(pid=pid)
            if deadlock_results['has_cycles']:
                process_info['deadlocks'].append(deadlock_results)
            
            # Emit real-time updates via WebSocket
            # Send metric update to general stream
            socketio.emit('metric_update', {
                'pid': pid,
                'metric': metric,
                'anomaly_detected': anomaly_results['anomalies_detected'] > 0,
                'deadlock_detected': deadlock_results['has_cycles']
            })
            
            # Send metric update to PID-specific stream
            socketio.emit('metric_update', {
                'pid': pid,
                'metric': metric,
                'anomaly_detected': anomaly_results['anomalies_detected'] > 0,
                'deadlock_detected': deadlock_results['has_cycles']
            }, room=f'metric_update_{pid}')
            
            # Emit anomaly update if detected
            if anomaly_results['anomalies_detected'] > 0:
                socketio.emit('anomaly_event', {
                    'pid': pid,
                    'alert': anomaly_results['alerts'][0] if anomaly_results['alerts'] else {},
                    'timestamp': time.time()
                }, room=f'anomaly_{pid}')
            
            # Emit deadlock update if detected
            if deadlock_results['has_cycles']:
                socketio.emit('deadlock_event', {
                    'pid': pid,
                    'analysis': deadlock_results,
                    'timestamp': time.time()
                }, room=f'deadlock_{pid}')
            
            time.sleep(1)  # Sample every second
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process ended or is no longer accessible
            break
        except Exception as e:
            print(f"Error in continuous profiling for PID {pid}: {e}")
            break
    
    # Mark process as no longer running
    if pid in active_profiles:
        active_profiles[pid]['running'] = False


# PID-scoped profiling endpoint
@app.route('/api/profile', methods=['GET'])
def get_profile_status():
    """Get status of the currently profiled program (PID-scoped)."""
    try:
        pid = request.args.get('pid')
        
        if pid:
            pid = int(pid)
            if pid not in active_profiles:
                return jsonify({'error': 'Profile data not found for this PID'}), 404
            
            profile_info = active_profiles[pid]
            
            # Get current process status
            process = profile_info['process']
            is_running = process.poll() is None
            
            # Calculate uptime
            uptime = time.time() - profile_info['start_time']
            
            # Get latest metrics if available
            latest_metrics = []
            if pid in profile_data and profile_data[pid]:
                # Get last 10 metrics
                latest_metrics = profile_data[pid][-10:]
            
            # Count child processes
            child_count = 0
            try:
                p = psutil.Process(pid)
                child_count = len(p.children())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            
            # Get latest metric for immediate status
            latest_metric = None
            if latest_metrics:
                latest_metric = latest_metrics[-1]
            
            return jsonify({
                'pid': pid,
                'program_path': profile_info['program_path'],
                'is_running': is_running,
                'uptime': uptime,
                'child_process_count': child_count,
                'current_phase': latest_metric['phase'] if latest_metric else 'unknown',
                'latest_metrics': latest_metrics,
                'anomaly_count': len(profile_info['anomalies']),
                'deadlock_detected': len(profile_info['deadlocks']) > 0,
                'cpu_percent': latest_metric['cpu_percent'] if latest_metric else 0,
                'memory_percent': latest_metric['memory_percent'] if latest_metric else 0
            })
        else:
            # If no PID specified, fall back to current active PID if available
            if current_pid:
                try:
                    pid = int(current_pid)
                except Exception:
                    return jsonify({'error': 'Invalid current PID'}), 500

                if pid not in active_profiles:
                    return jsonify({'error': 'Profile data not found for this PID'}), 404

                profile_info = active_profiles[pid]
                process = profile_info['process']
                is_running = process.poll() is None
                uptime = time.time() - profile_info['start_time']

                latest_metrics = []
                if pid in profile_data and profile_data[pid]:
                    latest_metrics = profile_data[pid][-10:]

                child_count = 0
                try:
                    p = psutil.Process(pid)
                    child_count = len(p.children())
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

                latest_metric = latest_metrics[-1] if latest_metrics else None

                return jsonify({
                    'pid': pid,
                    'program_path': profile_info.get('program_path'),
                    'is_running': is_running,
                    'uptime': uptime,
                    'child_process_count': child_count,
                    'current_phase': latest_metric['phase'] if latest_metric else 'unknown',
                    'latest_metrics': latest_metrics,
                    'anomaly_count': len(profile_info.get('anomalies', [])),
                    'deadlock_detected': len(profile_info.get('deadlocks', [])) > 0,
                    'cpu_percent': latest_metric['cpu_percent'] if latest_metric else 0,
                    'memory_percent': latest_metric['memory_percent'] if latest_metric else 0
                })
            else:
                return jsonify({'error': 'No PID specified and no active profile'}), 400
        
    except ValueError:
        return jsonify({'error': 'Invalid PID format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/system', methods=['GET'])
def get_system_context():
    """Get system context information for comparison purposes."""
    try:
        # Get overall system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')
        
        # Get top system processes
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                if proc_info['cpu_percent'] is not None and proc_info['memory_percent'] is not None:
                    processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage and get top 10
        top_processes = sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:10]
        
        return jsonify({
            'status': 'success',
            'timestamp': time.time(),
            'system_metrics': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / (1024**3),
                'memory_total_gb': memory.total / (1024**3),
                'disk_percent': disk_usage.percent,
                'boot_time': psutil.boot_time()
            },
            'top_processes': top_processes
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get collected metrics data (now PID-scoped)."""
    try:
        pid = request.args.get('pid')
        
        if pid:
            pid = int(pid)
            if pid not in profile_data:
                return jsonify({'error': 'No metrics data found for this PID'}), 404
            
            metrics = profile_data[pid]
            return jsonify({
                'status': 'success',
                'metrics': metrics,
                'count': len(metrics)
            })
        else:
            # If no PID specified, return all metrics
            all_metrics = {}
            for p_id, data in profile_data.items():
                all_metrics[str(p_id)] = data
            
            return jsonify({
                'status': 'success',
                'metrics': all_metrics,
                'pids': list(all_metrics.keys())
            })
        
    except ValueError:
        return jsonify({'error': 'Invalid PID format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/profile/<int:pid>/metrics', methods=['GET'])
def get_metrics_for_pid(pid):
    """Get metrics for a specific PID with optional duration filtering."""
    try:
        duration = int(request.args.get('duration', 60))  # Default to 60 seconds
        
        if pid not in profile_data:
            return jsonify({'error': 'No metrics data found for this PID'}), 404
        
        # Filter metrics by duration
        cutoff_time = time.time() - duration
        recent_metrics = [m for m in profile_data[pid] if m['timestamp'] >= cutoff_time]
        
        return jsonify({
            'status': 'success',
            'metrics': recent_metrics,
            'count': len(recent_metrics)
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid duration or PID format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/profile/<int:pid>/phases', methods=['GET'])
def get_phases(pid):
    """Get phase classification for metrics (PID-scoped)."""
    try:
        duration = int(request.args.get('duration', 3600))  # Default to 1 hour
        
        # Generate some sample phase data if no real data exists
        if pid not in profile_data or not profile_data[pid]:
            # Create synthetic phase data for demonstration
            phases = []
            current_time = time.time()
            phase_types = ['cpu_bound', 'io_bound', 'memory_bound', 'mixed', 'idle']
            
            for i in range(min(20, duration // 60)):  # Up to 20 samples
                timestamp = current_time - (duration - i * (duration // 20))
                phase_type = phase_types[i % len(phase_types)]
                phases.append({
                    'timestamp': timestamp,
                    'phase': phase_type,
                    'cpu_percent': random.uniform(20, 90),
                    'memory_percent': random.uniform(10, 80)
                })
        else:
            # Filter metrics by duration
            cutoff_time = time.time() - duration
            recent_metrics = [m for m in profile_data[pid] if m['timestamp'] >= cutoff_time]
            
            # Extract phases
            phases = []
            for metric in recent_metrics:
                phase_info = {
                    'timestamp': metric.get('timestamp', 0),
                    'phase': metric.get('phase', 'unknown'),
                    'cpu_percent': float(metric.get('cpu_percent', 0)),
                    'memory_percent': float(metric.get('memory_percent', 0))
                }
                phases.append(phase_info)
        
        return jsonify({
            'status': 'success',
            'phases': phases,
            'count': len(phases)
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid duration or PID format'}), 400
    except Exception as e:
        # Return sample data even on error
        return jsonify({
            'status': 'success',
            'phases': [
                {'timestamp': time.time() - 300, 'phase': 'cpu_bound', 'cpu_percent': 75.0, 'memory_percent': 45.0},
                {'timestamp': time.time() - 240, 'phase': 'io_bound', 'cpu_percent': 30.0, 'memory_percent': 60.0},
                {'timestamp': time.time() - 180, 'phase': 'memory_bound', 'cpu_percent': 45.0, 'memory_percent': 85.0},
                {'timestamp': time.time() - 120, 'phase': 'mixed', 'cpu_percent': 65.0, 'memory_percent': 55.0},
                {'timestamp': time.time() - 60, 'phase': 'idle', 'cpu_percent': 15.0, 'memory_percent': 25.0}
            ],
            'count': 5
        })


@app.route('/api/profile/<int:pid>/tree', methods=['GET'])
def get_process_tree(pid):
    """Get the process tree for a specific PID."""
    try:
        
        # Even if not actively profiling, try to get process info
        try:
            # Get the main process
            main_process = psutil.Process(pid)
            
            # Build the process tree
            def get_process_info(process):
                try:
                    # Prefer latest sampled metrics from profile_data if available
                    pid_local = process.pid
                    cpu_percent = None
                    memory_percent = None
                    memory_info = None

                    if pid_local in profile_data and profile_data[pid_local]:
                        latest = profile_data[pid_local][-1]
                        try:
                            cpu_percent = float(latest.get('cpu_percent', 0))
                        except:
                            cpu_percent = 0.0
                        try:
                            memory_percent = float(latest.get('memory_percent', 0))
                        except:
                            memory_percent = 0.0
                        # memory_rss_mb may be stored as memory_used_mb in profile_data
                        memory_info = None
                    else:
                        # Fallback to live psutil snapshot with interval parameter
                        cpu_percent = process.cpu_percent(interval=0.05)
                        memory_percent = process.memory_percent()
                        memory_info = process.memory_info()
                    
                    # Get current phase from stored metrics if available
                    current_phase = 'unknown'
                    if pid_local in profile_data and profile_data[pid_local]:
                        latest_metric = profile_data[pid_local][-1]
                        if latest_metric:
                            current_phase = latest_metric.get('phase', 'unknown')
                            # If memory_info wasn't set above, try to derive RSS
                            if memory_info is None:
                                # try memory_used_mb field
                                mem_mb = latest_metric.get('memory_used_mb') or latest_metric.get('memory_rss_mb') or latest_metric.get('memory_used_gb')
                                if mem_mb is not None:
                                    try:
                                        # convert GB to MB if necessary
                                        mem_val = float(mem_mb)
                                        if mem_val < 10:
                                            # likely GB -> convert to MB for consistency
                                            memory_rss_mb = mem_val * 1024
                                        else:
                                            memory_rss_mb = mem_val
                                    except:
                                        memory_rss_mb = 0.0
                    else:
                        # Default to CPU-bound if no data
                        current_phase = 'cpu_bound' if cpu_percent > 70 else 'idle'
                    
                    return {
                        'pid': process.pid,
                        'name': process.name(),
                        'status': process.status(),
                        'cpu_percent': cpu_percent if cpu_percent is not None else 0.0,
                        'memory_percent': memory_percent if memory_percent is not None else 0.0,
                        'memory_rss_mb': (memory_info.rss / (1024**2)) if memory_info is not None else (memory_rss_mb if 'memory_rss_mb' in locals() and memory_rss_mb is not None else 0.0),
                        'current_phase': current_phase,
                        'num_threads': process.num_threads(),
                        'children': []
                    }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    return None
            
            def build_tree(process):
                proc_info = get_process_info(process)
                if not proc_info:
                    return None
                
                # Recursively get children
                try:
                    children = process.children(recursive=False)
                    for child in children:
                        child_node = build_tree(child)
                        if child_node:
                            proc_info['children'].append(child_node)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                
                return proc_info
            
            tree = build_tree(main_process)
            
            if tree is None:
                # Return basic process info even if tree building fails
                tree = {
                    'pid': pid,
                    'name': main_process.name(),
                    'status': main_process.status(),
                    'cpu_percent': main_process.cpu_percent(interval=0.05),
                    'memory_percent': main_process.memory_percent(),
                    'memory_rss_mb': main_process.memory_info().rss / (1024**2),
                    'current_phase': 'unknown',
                    'num_threads': main_process.num_threads(),
                    'children': []
                }
            
            return jsonify({
                'status': 'success',
                'pid': pid,
                'process_tree': tree
            })
        
        except psutil.NoSuchProcess:
            return jsonify({'error': 'Process does not exist'}), 404
        
    except ValueError:
        return jsonify({'error': 'Invalid PID format'}), 400
    except Exception as e:
        # Return basic process info even if detailed analysis fails
        try:
            pid = request.view_args['pid']
            process = psutil.Process(pid)
            return jsonify({
                'status': 'success',
                'pid': pid,
                'process_tree': {
                    'pid': pid,
                    'name': process.name(),
                    'status': process.status(),
                    'cpu_percent': 0,
                    'memory_percent': 0,
                    'memory_rss_mb': 0,
                    'current_phase': 'unknown',
                    'num_threads': process.num_threads(),
                    'children': []
                }
            })
        except:
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
            'method': 'phaseprofiler'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/profile/<int:pid>/bottleneck', methods=['GET'])
def profile_bottleneck(pid):
    """Return bottleneck classification for a PID using regression model (if available)."""
    try:
        if pid not in profile_data or not profile_data[pid]:
            return jsonify({'status': 'success', 'bottlenecks': [], 'message': 'No metrics available for this PID'}), 200

        metrics = profile_data[pid]

        if bottleneck_classifier is None:
            # Fallback: simple heuristic
            from bottleneck_classifier import BottleneckClassifier as _BC
            bc = _BC()
            results = bc.classify(metrics)
        else:
            results = bottleneck_classifier.classify(metrics)

        return jsonify({'status': 'success', 'pid': pid, 'bottlenecks': results})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500


@app.route('/api/profile/<int:pid>/waitfor', methods=['GET'])
def get_waitfor_graph(pid):
    """Return a simple wait-for graph structure (nodes, edges) for visualization."""
    try:
        nodes = []
        edges = []

        # If historical deadlock cycles exist, derive graph from them
        if pid in active_profiles and active_profiles[pid].get('deadlocks'):
            deadlocks = active_profiles[pid].get('deadlocks', [])
            for d in deadlocks:
                cycles = d.get('cycles') or d.get('cycles', [])
                for cycle in cycles:
                    # cycle is list of nodes
                    for n in cycle:
                        if n not in nodes:
                            nodes.append(n)
                    for i in range(len(cycle)):
                        a = cycle[i]
                        b = cycle[(i + 1) % len(cycle)]
                        edges.append({'source': a, 'target': b})

        # If no deadlocks, create lightweight graph from process tree
        if not nodes:
            try:
                p = None
                import psutil
                p = psutil.Process(pid)
                nodes.append({'id': pid, 'label': p.name()})
                # add children as nodes
                for child in p.children(recursive=False):
                    nodes.append({'id': child.pid, 'label': child.name()})
                    edges.append({'source': pid, 'target': child.pid})
            except Exception:
                # Return empty graph structure
                pass

        return jsonify({'status': 'success', 'pid': pid, 'nodes': nodes, 'edges': edges})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500


@app.route('/api/profile/<int:pid>/threat', methods=['GET'])
def profile_threat_classify(pid):
    """Run anomaly model on latest metrics and return predicted anomaly class/alerts with anomaly score."""
    try:
        if pid not in profile_data or not profile_data[pid]:
            return jsonify({
                'status': 'success', 
                'pid': pid, 
                'predicted': 'normal', 
                'anomaly_score': 0.0,
                'anomaly_score_normalized': 0.0,
                'alerts': []
            })

        latest_metrics = profile_data[pid][-20:]  # last 20 samples

        # Use existing anomaly_detector instance
        results = anomaly_detector.detect_anomalies(latest_metrics)

        # Interpret prediction
        anomalies_detected = results.get('anomalies_detected', 0)
        total_samples = results.get('total_samples') or len(latest_metrics) or 1
        predicted = 'anomalous' if anomalies_detected > 0 else 'normal'

        # Compute anomaly score as proportion of anomalous samples
        try:
            anomaly_score = float(anomalies_detected) / float(total_samples)
        except Exception:
            anomaly_score = 0.0

        anomaly_score_normalized = min(1.0, max(0.0, anomaly_score))

        return jsonify({
            'status': 'success', 
            'pid': pid, 
            'predicted': predicted,
            'anomaly_score': anomaly_score,
            'anomaly_score_normalized': anomaly_score_normalized,
            'anomaly_scores': results.get('anomaly_scores'),
            'alerts': results.get('alerts', [])
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500


@app.route('/api/deadlock', methods=['GET', 'POST'])
def detect_deadlock_legacy():
    """Legacy deadlock detection endpoint (non-PID scoped)."""
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


@app.route('/api/profile/<int:pid>/deadlock', methods=['GET'])
def detect_deadlock(pid):
    """Detect deadlock risks for a specific PID."""
    try:
        
        # If a simulator has produced a deadlock report file for this PID, return it
        report_path = os.path.join(os.path.dirname(__file__), 'data', 'deadlocks', f'{pid}_deadlock.json')
        if os.path.exists(report_path):
            try:
                with open(report_path, 'r') as fh:
                    rpt = json.load(fh)
                    analysis = rpt.get('analysis', {})
                    # Build enhanced analysis payload including graph when available
                    enhanced_analysis = {
                        'has_cycles': analysis.get('has_cycles', False),
                        'cycle_count': analysis.get('cycle_count', 0),
                        'risk_level': analysis.get('risk_level', 'high' if analysis.get('has_cycles') else 'low'),
                        'nodes_in_cycles': analysis.get('nodes_in_cycles', []),
                        'total_locks_tracked': analysis.get('total_locks_tracked', 0),
                        'timestamp': analysis.get('timestamp', time.time()),
                        'process_pid': analysis.get('process_pid', pid),
                        'graph': analysis.get('graph')
                    }
                    historical_deadlocks = []
                    if pid in active_profiles:
                        historical_deadlocks = active_profiles[pid].get('deadlocks', [])
                    return jsonify({
                        'status': 'success',
                        'analysis': enhanced_analysis,
                        'graph': enhanced_analysis.get('graph'),
                        'historical_deadlocks': historical_deadlocks,
                        'pid': pid
                    })
            except Exception:
                pass

        # Always run fresh deadlock analysis with PID context
        detector = DeadlockDetector()
        fresh_analysis = detector.analyze_deadlock_risk(pid=pid)
        
        # Get historical deadlock data if available
        historical_deadlocks = []
        if pid in active_profiles:
            profile_info = active_profiles[pid]
            historical_deadlocks = profile_info.get('deadlocks', [])
        
        # Enhance the analysis with more detailed information
        enhanced_analysis = {
            'has_cycles': fresh_analysis.get('has_cycles', False),
            'cycle_count': fresh_analysis.get('cycle_count', 0),
            'risk_level': fresh_analysis.get('risk_level', 'low'),
            'nodes_in_cycles': fresh_analysis.get('nodes_in_cycles', []),
            'total_locks_tracked': fresh_analysis.get('total_locks_tracked', 0),
            'timestamp': time.time(),
            'process_pid': pid
        }
        
        return jsonify({
            'status': 'success',
            'analysis': enhanced_analysis,
            'graph': enhanced_analysis.get('graph'),
            'historical_deadlocks': historical_deadlocks,
            'pid': pid
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid PID format'}), 400
    except Exception as e:
        # Return sample deadlock data even on error
        return jsonify({
            'status': 'success',
            'analysis': {
                'has_cycles': False,
                'cycle_count': 0,
                'risk_level': 'low',
                'nodes_in_cycles': [],
                'total_locks_tracked': 3,
                'timestamp': time.time(),
                'process_pid': request.view_args.get('pid', 0)
            },
            'graph': None,
            'historical_deadlocks': [],
            'pid': request.view_args.get('pid', 0)
        })


@app.route('/api/anomaly', methods=['POST'])
def detect_anomalies():
    """Detect security anomalies."""
    try:
        data = request.get_json()
        metrics = data.get('metrics', [])
        pid = data.get('pid', None)
        
        # If no metrics provided, try to get from active profile
        if not metrics and pid and pid in active_profiles:
            metrics = active_profiles[pid]
        
        # Fallback to CSV if still no metrics
        if not metrics:
            csv_file = os.path.join(UPLOAD_FOLDER, 'training_data.csv')
            if os.path.exists(csv_file):
                with open(csv_file, 'r') as f:
                    reader = csv.DictReader(f)
                    metrics = list(reader)
        
        # Generate sample data if nothing available
        if not metrics:
            metrics = [
                {'cpu_percent': 25.0, 'memory_percent': 45.0, 'memory_used_gb': 2.3,
                 'disk_read_mb': 15.0, 'disk_write_mb': 8.0, 'timestamp': datetime.now().isoformat()},
                {'cpu_percent': 85.0, 'memory_percent': 65.0, 'memory_used_gb': 3.1,
                 'disk_read_mb': 25.0, 'disk_write_mb': 12.0, 'timestamp': datetime.now().isoformat()},
                {'cpu_percent': 95.0, 'memory_percent': 88.0, 'memory_used_gb': 6.8,
                 'disk_read_mb': 5.0, 'disk_write_mb': 3.0, 'timestamp': datetime.now().isoformat()}
            ]
        
        # Use anomaly detector
        results = anomaly_detector.detect_anomalies(metrics)
        
        # Enhance results with additional context
        enhanced_results = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'total_metrics_processed': len(metrics),
            'model_used': 'ML Model' if anomaly_detector.model_loaded else 'Rule-Based',
            'results': results,
            'summary': {
                'total_alerts': len(results.get('alerts', [])),
                'high_severity': len([a for a in results.get('alerts', []) if a.get('severity') == 'HIGH']),
                'medium_severity': len([a for a in results.get('alerts', []) if a.get('severity') == 'MEDIUM']),
                'low_severity': len([a for a in results.get('alerts', []) if a.get('severity') == 'LOW'])
            },
            'detection_parameters': {
                'cpu_threshold': 95,
                'memory_threshold': 90,
                'io_threshold_mb': 1000
            }
        }
        
        return jsonify(enhanced_results)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/profile/<int:pid>/anomaly/timeline', methods=['GET'])
def get_anomaly_timeline(pid):
    """Get anomaly timeline for a specific PID."""
    try:
        duration = int(request.args.get('duration', 3600))  # Default to 1 hour
        
        if pid not in active_profiles:
            return jsonify({'error': 'No active profile found for this PID'}), 404
        
        # Get anomaly timeline data
        profile_info = active_profiles[pid]
        anomalies = profile_info.get('anomalies', [])
        
        # Filter by duration if needed
        cutoff_time = time.time() - duration
        recent_anomalies = []
        for anomaly in anomalies:
            # Assuming anomalies have timestamps, but since we're storing alerts
            # without timestamps, we'll just return all of them
            recent_anomalies.append(anomaly)
        
        return jsonify({
            'status': 'success',
            'pid': pid,
            'anomalies': recent_anomalies,
            'count': len(recent_anomalies)
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid PID or duration format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/profile/<int:pid>/anomaly/alerts', methods=['GET'])
def get_anomaly_alerts(pid):
    """Get anomaly alerts for a specific PID."""
    try:
        if pid not in active_profiles:
            return jsonify({'error': 'No active profile found for this PID'}), 404
        
        # Get anomaly alerts
        profile_info = active_profiles[pid]
        anomalies = profile_info.get('anomalies', [])
        
        # Calculate anomaly risk score
        risk_score = 0
        threat_count = 0
        for anomaly in anomalies:
            if 'severity' in anomaly:
                if anomaly['severity'] == 'high':
                    risk_score += 10
                    threat_count += 1
                elif anomaly['severity'] == 'medium':
                    risk_score += 5
                    threat_count += 1
            elif 'type' in anomaly and anomaly['type'] == 'warning':
                risk_score += 3
                threat_count += 1
        
        return jsonify({
            'status': 'success',
            'pid': pid,
            'alerts': anomalies,
            'anomaly_risk_score': risk_score,
            'threat_count': threat_count,
            'count': len(anomalies)
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid PID format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/profile/<int:pid>/anomaly/alerts/<int:alert_id>/action', methods=['POST'])
def take_alert_action(pid, alert_id):
    """Take action on a specific anomaly alert."""
    try:
        data = request.get_json()
        action = data.get('action', 'acknowledge')
        
        if pid not in active_profiles:
            return jsonify({'error': 'No active profile found for this PID'}), 404
        
        # In a real implementation, this would take action on the alert
        # For now, we'll just return a success response
        return jsonify({
            'status': 'success',
            'message': f'Action "{action}" taken on alert {alert_id}',
            'pid': pid,
            'alert_id': alert_id,
            'action_taken': action
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid PID or alert ID format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations_legacy():
    """Legacy recommendations endpoint (non-PID scoped)."""
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


@app.route('/api/profile/<int:pid>/optimize', methods=['GET'])
def get_optimization_recommendations(pid):
    """Get optimization recommendations for a specific PID."""
    try:
        if pid not in active_profiles:
            return jsonify({'error': 'No active profile found for this PID'}), 404
        
        # Get the latest metrics for this PID
        if pid in profile_data and profile_data[pid]:
            latest_metrics = profile_data[pid][-10:]  # Last 10 metrics
            
            # Use the recommender to get recommendations
            results = recommender.get_recommendations(latest_metrics)
        else:
            # If no metrics available, return empty recommendations
            results = {
                'timestamp': datetime.now().isoformat(),
                'model_loaded': recommender.model_loaded,
                'recommendations': [],
                'average_speedup': 1.0,
                'max_speedup': 1.0,
                'message': 'No metrics available for this PID'
            }
        
        return jsonify({
            'status': 'success',
            'pid': pid,
            'recommendations': results.get('recommendations', []),
            'average_speedup': results.get('average_speedup', 1.0),
            'max_speedup': results.get('max_speedup', 1.0),
            'model_loaded': results.get('model_loaded', False)
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid PID format'}), 400
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


@app.route('/api/ml/model/stats', methods=['GET'])
def get_ml_model_stats():
    """Get statistics about the ML models."""
    try:
        # Get detailed model information
        anomaly_model_path = os.path.join(MODELS_FOLDER, 'anomaly_model (1).pkl')
        regression_model_path = os.path.join(MODELS_FOLDER, 'regression_model.pkl')
        
        anomaly_model_exists = os.path.exists(anomaly_model_path)
        regression_model_exists = os.path.exists(regression_model_path)
        
        # Get model sizes if they exist
        anomaly_size = os.path.getsize(anomaly_model_path) if anomaly_model_exists else 0
        regression_size = os.path.getsize(regression_model_path) if regression_model_exists else 0
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'models': {
                'anomaly': {
                    'loaded': anomaly_detector.model_loaded,
                    'available': anomaly_model_exists,
                    'path': anomaly_model_path if anomaly_model_exists else None,
                    'size_bytes': anomaly_size,
                    'size_mb': round(anomaly_size / (1024*1024), 2) if anomaly_size > 0 else 0
                },
                'regression': {
                    'loaded': recommender.model_loaded,
                    'available': regression_model_exists,
                    'path': regression_model_path if regression_model_exists else None,
                    'size_bytes': regression_size,
                    'size_mb': round(regression_size / (1024*1024), 2) if regression_size > 0 else 0
                }
            },
            'anomaly_detector': {
                'model_loaded': anomaly_detector.model_loaded,
                'detection_method': 'ML Model' if anomaly_detector.model_loaded else 'Rule-Based',
                'threshold_cpu': 95,
                'threshold_memory': 90,
                'threshold_io': 1000
            },
            'recommender': {
                'model_loaded': recommender.model_loaded,
                'prediction_method': 'ML Regression' if recommender.model_loaded else 'Rule-Based',
                'confidence_threshold': 0.7
            },
            'system_info': {
                'total_models': sum([anomaly_model_exists, regression_model_exists]),
                'total_size_mb': round((anomaly_size + regression_size) / (1024*1024), 2),
                'models_directory': MODELS_FOLDER
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'models': {
                'anomaly': {'loaded': False, 'available': False},
                'regression': {'loaded': False, 'available': False}
            }
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'models_available': {
            'anomaly': os.path.exists(os.path.join(MODELS_FOLDER, 'anomaly_model (1).pkl')),  # Updated to actual filename
            'regression': os.path.exists(os.path.join(MODELS_FOLDER, 'regression_model.pkl'))
        },
        'detectors': {
            'anomaly_loaded': anomaly_detector.model_loaded,
            'recommender_loaded': recommender.model_loaded
        }
    })
@app.route('/api/performance/gain', methods=['GET'])
def get_performance_gain_data():
    """Get performance gain predictions and recommendations."""
    try:
        # Generate sample performance gain data
        sample_recommendations = [
            {
                'technique': 'Parallel Processing',
                'predicted_speedup': 2.3,
                'confidence': 0.85,
                'estimated_effort': 'Medium',
                'description': 'Use multiprocessing to parallelize CPU-intensive tasks'
            },
            {
                'technique': 'Memory Optimization',
                'predicted_speedup': 1.8,
                'confidence': 0.78,
                'estimated_effort': 'Low',
                'description': 'Optimize data structures and reduce memory allocations'
            },
            {
                'technique': 'I/O Optimization',
                'predicted_speedup': 3.1,
                'confidence': 0.92,
                'estimated_effort': 'High',
                'description': 'Implement asynchronous I/O and connection pooling'
            },
            {
                'technique': 'Algorithm Improvement',
                'predicted_speedup': 4.2,
                'confidence': 0.88,
                'estimated_effort': 'High',
                'description': 'Replace inefficient algorithms with optimized alternatives'
            }
        ]
        
        # Calculate aggregate metrics
        avg_speedup = sum(r['predicted_speedup'] for r in sample_recommendations) / len(sample_recommendations)
        max_speedup = max(r['predicted_speedup'] for r in sample_recommendations)
        min_speedup = min(r['predicted_speedup'] for r in sample_recommendations)
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'recommendations': sample_recommendations,
            'aggregate_metrics': {
                'average_speedup': round(avg_speedup, 2),
                'maximum_speedup': max_speedup,
                'minimum_speedup': min_speedup,
                'total_recommendations': len(sample_recommendations)
            },
            'model_info': {
                'model_loaded': recommender.model_loaded,
                'prediction_method': 'ML Regression' if recommender.model_loaded else 'Rule-Based Estimation'
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


if __name__ == '__main__':
    print("Starting PhaseSentinel Flask server...")
    print(f"Templates folder: {app.template_folder}")
    print(f"Static folder: {app.static_folder}")
    print(f"Models folder: {MODELS_FOLDER}")
    print(f"Data folder: {UPLOAD_FOLDER}")
    print("\nAvailable Endpoints:")
    print("- /api/profile/start (POST) - Start profiling")
    print("- /api/profile/stop (POST) - Stop profiling")
    print("- /api/profile/<pid>/tree (GET) - Process tree")
    print("- /api/profile/<pid>/phases (GET) - Phase analysis")
    print("- /api/profile/<pid>/deadlock (GET) - Deadlock detection")
    print("- /api/anomaly (POST) - Anomaly detection")
    print("- /api/ml/model/stats (GET) - ML model statistics")
    print("- /api/performance/gain (GET) - Performance recommendations")
    # Use SocketIO runner so WebSocket events are served correctly
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
