"""
Bottleneck classifier helper
Loads a pre-trained regression model (if available) and provides a classify() helper
that returns CPU/Memory/I/O bottleneck classifications for a PID's recent metrics.
"""
import os
import joblib
import numpy as np
from datetime import datetime


class BottleneckClassifier:
    def __init__(self, model_path=None):
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        if model_path is None:
            model_path = os.path.join(backend_dir, 'models', 'regression_model.pkl')
        self.model_path = model_path
        self.model = None
        self.model_loaded = False
        self._load()

    def _load(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                self.model_loaded = True
                print(f"Bottleneck regression model loaded from {self.model_path}")
            except Exception as e:
                print(f"Error loading regression model: {e}")
                self.model_loaded = False
        else:
            print(f"Regression model not found at {self.model_path}")

    def _extract_features(self, metrics):
        # Expect list of metric dicts; extract summary features per PID
        if not metrics:
            return np.array([[0, 0, 0]])

        cpu_vals = [float(m.get('cpu_percent', 0)) for m in metrics]
        mem_vals = [float(m.get('memory_percent', 0)) for m in metrics]
        io_vals = [float(m.get('disk_read_mb', 0)) + float(m.get('disk_write_mb', 0)) for m in metrics]

        features = [
            np.mean(cpu_vals),
            np.mean(mem_vals),
            np.mean(io_vals)
        ]

        return np.array([features])

    def classify(self, metrics):
        """
        Classify bottleneck type for provided metrics.

        Returns list of bottleneck dicts: {type, severity, message, duration}
        """
        try:
            features = self._extract_features(metrics)

            # Try using model if available
            if self.model_loaded and self.model is not None:
                try:
                    pred = None
                    # If model is classifier
                    if hasattr(self.model, 'predict'):
                        pred = self.model.predict(features)
                    # Map numeric predictions to bottleneck types if applicable
                    if pred is not None:
                        label = str(pred[0])
                        # Attempt to interpret common labels
                        if label.lower().startswith('cpu') or float(features[0][0]) > 70:
                            btype = 'CPU-bound'
                        elif label.lower().startswith('mem') or float(features[0][1]) > 70:
                            btype = 'Memory-bound'
                        else:
                            btype = 'I/O-bound'
                        severity = int(min(10, max(1, int(round((features[0][0] + features[0][1]) / 20)))))
                        return [{
                            'type': btype,
                            'severity': severity,
                            'message': f'Predicted by regression model: {label}',
                            'duration': None
                        }]
                except Exception:
                    # Fallback to heuristic below
                    pass

            # Heuristic fallback
            cpu_avg = features[0][0]
            mem_avg = features[0][1]
            io_avg = features[0][2]

            # Determine dominant resource
            if cpu_avg >= mem_avg and cpu_avg >= io_avg:
                btype = 'CPU-bound'
                severity = int(min(10, max(3, int(cpu_avg / 10))))
                message = f'Average CPU {cpu_avg:.1f}% indicates CPU-bound behavior.'
            elif mem_avg >= cpu_avg and mem_avg >= io_avg:
                btype = 'Memory-bound'
                severity = int(min(10, max(3, int(mem_avg / 10))))
                message = f'Average memory {mem_avg:.1f}% indicates memory pressure.'
            else:
                btype = 'I/O-bound'
                severity = int(min(10, max(3, int(min(10, io_avg / 10)))))
                message = f'Average I/O {io_avg:.1f}MB indicates I/O bottleneck.'

            return [{
                'type': btype,
                'severity': severity,
                'message': message,
                'duration': None
            }]
        except Exception as e:
            return [{
                'type': 'unknown',
                'severity': 0,
                'message': f'Error classifying bottleneck: {e}',
                'duration': None
            }]


if __name__ == '__main__':
    # simple self-test
    bc = BottleneckClassifier()
    print(bc.classify([{'cpu_percent': 85, 'memory_percent': 40, 'disk_read_mb': 1, 'disk_write_mb': 0}]))
