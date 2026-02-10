"""
Train Anomaly Detection Model from final.csv
Uses Isolation Forest for anomaly detection
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Load data
print("Loading final.csv...")
df = pd.read_csv('data/final.csv')
print(f"Loaded {len(df)} samples")
print(f"Columns: {df.columns.tolist()}")
print(f"\nData preview:")
print(df.head(10))

# Check for missing values
print(f"\nMissing values:\n{df.isnull().sum()}")

# Drop rows with missing values
print("\nRemoving rows with missing values...")
df = df.dropna()

# Remove header rows that appear in data (if any)
df = df[(df['label'] != 'label') & (df['cpu'] != 'cpu')]

# Convert to numeric types
df['cpu'] = pd.to_numeric(df['cpu'], errors='coerce')
df['memory'] = pd.to_numeric(df['memory'], errors='coerce')
df['disk_io'] = pd.to_numeric(df['disk_io'], errors='coerce')

# Drop rows with NaN after conversion
df = df.dropna()
print(f"After cleaning: {len(df)} samples")

# Extract features (cpu, memory, disk_io)
X = df[['cpu', 'memory', 'disk_io']].values
y = df['label'].values

print(f"\nFeature shape: {X.shape}")
print(f"Unique labels: {np.unique(y)}")
print(f"Label distribution:\n{pd.Series(y).value_counts()}")

# Standardize features for better model performance
print("\nStandardizing features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train Isolation Forest model
print("\nTraining Isolation Forest model...")
model = IsolationForest(
    contamination=0.1,  # Assume ~10% of data is anomalies
    random_state=42,
    n_estimators=100,
    max_samples='auto',
    max_features=1.0,
    n_jobs=-1
)

model.fit(X_scaled)

# Evaluate on training data
predictions = model.predict(X_scaled)
anomaly_count = (predictions == -1).sum()
normal_count = (predictions == 1).sum()

print(f"\nModel Predictions:")
print(f"  Anomalies detected: {anomaly_count}")
print(f"  Normal samples: {normal_count}")

# Compare with actual labels
actual_anomalies = (y == 'anomaly').sum()
actual_normals = (y == 'normal').sum()
print(f"\nActual Labels:")
print(f"  Anomalies: {actual_anomalies}")
print(f"  Normal: {actual_normals}")

# Create models directory if it doesn't exist
os.makedirs('models', exist_ok=True)

# Save the model
model_path = 'models/anomaly_model (1).pkl'
print(f"\nSaving model to {model_path}...")
joblib.dump(model, model_path)

# Also save the scaler for later use
scaler_path = 'models/anomaly_scaler.pkl'
joblib.dump(scaler, scaler_path)

print(f"✅ Model saved: {model_path}")
print(f"✅ Scaler saved: {scaler_path}")
print(f"\nModel training complete!")
