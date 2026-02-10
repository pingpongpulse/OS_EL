# Simulation Programs Documentation

This directory contains various malicious and anomalous program simulations for testing PhaseSentinel's detection capabilities.

## Available Simulations

### 1. **Crypto Miner** (`crypto_miner.py`)
Simulates a cryptocurrency mining process

**Characteristics:**
- High sustained CPU usage (80-95%)
- Steady memory consumption
- Multiple worker processes utilizing all CPU cores
- Continuous SHA256 hashing operations
- Anomaly Type: **CRYPTO_MINING**

**Usage:**
```bash
python crypto_miner.py [DURATION]
```

**Example:**
```bash
python crypto_miner.py 60  # Run for 60 seconds
```

**Expected Profiler Output:**
- CPU-bound anomaly detection
- High CPU utilization alerts
- Thread analysis showing multiple workers
- Predicted anomaly: ANOMALOUS

---

### 2. **Memory Leak** (`memory_leak.py`)
Simulates a memory leak vulnerability

**Characteristics:**
- Continuously allocates memory without releasing
- Memory grows steadily over time
- Minimal CPU usage (5-10%)
- Accumulates both objects and string data
- Anomaly Type: **MEMORY_LEAK**

**Usage:**
```bash
python memory_leak.py [DURATION]
```

**Example:**
```bash
python memory_leak.py 60  # Run for 60 seconds
```

**Expected Profiler Output:**
- Rising memory usage patterns
- Memory-bound phase detection
- Potential memory leak warnings
- Steady memory growth anomaly detection

---

### 3. **Deadlock Simulation** (`deadlock_sim.py`)
Simulates a classic circular-wait deadlock scenario

**Characteristics:**
- Two threads competing for two locks
- Thread A: Lock A → Lock B
- Thread B: Lock B → Lock A
- Produces lock acquisition timeouts
- Demonstrates deadlock risk patterns
- Anomaly Type: **DEADLOCK**

**Usage:**
```bash
python deadlock_sim.py [DURATION]
```

**Example:**
```bash
python deadlock_sim.py 60  # Run for 60 seconds
```

**Expected Profiler Output:**
- Wait-for graph with cycles
- Deadlock detection alerts
- Lock wait analysis
- Risk level: MEDIUM/HIGH
- Thread synchronization recommendations

---

### 4. **Fork Bomb** (`fork_bomb.py`)
Simulates uncontrolled process creation

**Characteristics:**
- Rapidly creates child processes
- Resource exhaustion
- CPU and memory spikes
- High I/O overhead
- **⚠️ WARNING: Can impact system stability**

**Usage:** (Use with caution!)
```bash
python fork_bomb.py [DURATION]
```

---

### 5. **Leaky Program** (`leaky.py`)
Simulates various resource leaks

**Characteristics:**
- Multiple resource leak patterns
- File handle leaks
- Memory leaks
- Connection leaks

---

### 6. **Miner Simulation** (`miner_sim.py`)
Alternative crypto mining simulation

**Characteristics:**
- Similar to crypto_miner.py
- Different implementation approach

---

## How to Run Profiler on Simulations

### Step 1: Start PhaseSentinel
```bash
cd c:\Users\SATYA ADITYA INFRA\OS_EL\backend
python app.py
```

### Step 2: Open Dashboard
```
http://localhost:5000
```

### Step 3: Profile a Simulation

#### Option A: Using GUI
1. Click "Start Profiling" button
2. Enter program path: `backend/simulations/crypto_miner.py`
3. Set duration: 30 seconds
4. Click "Profile Now"
5. Observe anomaly detection in real-time

#### Option B: Using Command Line
```bash
# In another terminal, run while profiler is active
python backend/simulations/crypto_miner.py 30
```

### Step 4: View Results
After profiling completes, view:
- **Overview Tab**: Aggregated metrics
- **Execution Tab**: Phase analysis, deadlock detection
- **Intelligence Tab**: Anomaly classification, threat levels

---

## Testing Scenarios

### Scenario 1: Crypto Mining Detection
```bash
# Terminal 1
python app.py

# Terminal 2
# Start profiling for crypto_miner.py via dashboard

# Expected: High CPU detection, CRYPTO_MINING anomaly type
```

### Scenario 2: Memory Leak Detection
```bash
# Run memory_leak.py and observe:
# - Increasing memory usage over time
# - No corresponding increase in CPU
# - MEMORY_LEAK anomaly classification
```

### Scenario 3: Deadlock Detection
```bash
# Run deadlock_sim.py and observe:
# - Wait-for graph with visible cycles
# - Deadlock alerts in Concurrency Analysis
# - Lock contention analysis
# - Risk level ratings
```

### Scenario 4: Combined Anomalies
```bash
# Run multiple simulations together:
python crypto_miner.py 60 &
python memory_leak.py 60 &
python deadlock_sim.py 60 &

# Profile with 90-second duration
# Observe multiple concurrent anomalies
```

---

## Anomaly Detection Mapping

| Simulation | Anomaly Type | Detection Method |
|-----------|--------------|-----------------|
| crypto_miner.py | CRYPTO_MINING | High sustained CPU, multi-threaded |
| memory_leak.py | MEMORY_LEAK | Rising memory, low CPU |
| deadlock_sim.py | DEADLOCK | Lock cycles, thread waits |
| fork_bomb.py | RESOURCE_EXHAUSTION | Rapid process creation |
| leaky.py | RESOURCE_EXHAUSTION | Multiple leak types |

---

## Graph Behavior After Profiling Stops

When you click **Stop** or the profiling duration expires:

### ✅ Graph Persistence
- **Program Resource Usage** chart stops updating
- **Live Metrics (Last 60s)** chart stops updating
- **Anomaly Score Time-series** chart stops updating
- All data collected up to stop point is preserved

### 📊 Scrollable Graphs
- Graphs become horizontally scrollable
- Scroll left to view earlier time periods
- Scroll right to view most recent data
- Full profiling history remains visible

### 🔄 Analysis Display
- Deadlock analysis appears in Execution tab
- Anomaly classification in Intelligence tab
- Phase breakdown and bottleneck analysis
- All results persist until new profiling starts

---

## Performance Notes

- **Crypto Miner**: High CPU impact, visible on dashboard
- **Memory Leak**: Growing memory footprint, low CPU
- **Deadlock Sim**: Medium CPU, lock contention visible
- **Fork Bomb**: 🚨 Can severely impact system - avoid on production

---

## Troubleshooting

### Issue: Simulation doesn't show anomalies
**Solution:**
- Ensure profiler is running for full duration
- Check that simulation runs during profiling window
- Verify models are loaded in Intelligence tab

### Issue: Deadlock simulation doesn't show cycles
**Solution:**
- Run for at least 30 seconds
- Multiple threads may not always deadlock instantly
- Check browser console for errors

### Issue: Graphs don't stop updating
**Solution:**
- Verify profilingInProgress flag is working
- Check browser console (F12) for JS errors
- Refresh page and try again

### Issue: Can't see full graph history
**Solution:**
- Use horizontal scroll in chart containers
- Or, expand browser window width
- Charts auto-adjust to container size

---

## Advanced Usage

### Manually Testing Anomaly Detection
```python
import sys
sys.path.insert(0, 'backend')
from anomaly_detector import AnomalyDetector

detector = AnomalyDetector()
result = detector.predict([...metrics...])
```

### Checking Deadlock Detection
```python
from deadlock_detector_new import DeadlockDetector

detector = DeadlockDetector()
analysis = detector.analyze_deadlock_risk()
print(analysis['has_cycles'])  # True if deadlock found
```

---

## Contributing New Simulations

To add a new simulation:

1. Create `your_simulation.py` in this directory
2. Implement anomalous behavior
3. Add logging for debugging
4. Include command-line duration argument
5. Document expected anomaly types
6. Add to this README

---

## Safety Warnings

⚠️ **Use with Caution:**
- **fork_bomb.py** can crash your system - limit duration to 5-10 seconds
- Run on non-production systems when possible
- Monitor system resources while running tests
- Can create hundreds of processes - have process manager ready

---

**Last Updated:** 2026-02-09  
**Status:** All simulations tested and verified  
**Ready for profiling tests!** ✓

