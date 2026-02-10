# Complete Test Guide: Simulations & Graph Persistence

## 🎯 What's New

### 1. Three New Malicious Simulations Added
- ✅ **crypto_miner.py** - Simulates cryptocurrency mining (HIGH CPU)
- ✅ **memory_leak.py** - Simulates memory leak vulnerability (RISING MEMORY)
- ✅ **deadlock_sim.py** - Simulates deadlock condition (LOCK CYCLES)

### 2. Graph Persistence Improvements
- ✅ Graphs stop updating when profiling stops
- ✅ Charts remain on screen showing collected data
- ✅ Graphs are horizontally scrollable to view full timeline
- ✅ Data persistent during result analysis

---

## 📋 Prerequisites

```bash
# Ensure you're in the project root
cd c:\Users\SATYA ADITYA INFRA\OS_EL

# Install/update dependencies
cd backend
pip install -r requirements.txt

# Start Flask server
python app.py
# Should see: "Running on http://localhost:5000"
```

---

## 🧪 Test 1: Crypto Miner Simulation

### What to Test
High CPU usage detection with cryptocurrency mining anomaly classification

### Procedure

**Step 1: Open Dashboard**
```
http://localhost:5000
```

**Step 2: Start Profiling**
- Click "Start Profiling" button
- **Program Path**: `backend/simulations/crypto_miner.py`
- **Duration**: 30 seconds
- Click "Profile Now"

**Step 3: Observe Profiling (Real-time)**
✓ CPU usage jumps to 80-95%
✓ Memory stays stable (~5-10%)
✓ Process tree shows multiple worker processes
✓ Charts update continuously

**Step 4: Click Stop or Wait 30s**
When profiling stops:

✓ **Charts Stop Updating**: No new data points added
✓ **Program Resource Chart** persists showing:
  - CPU spike to 80-95%
  - Memory stable
  - Disk I/O minimal
  
✓ **View automatically switches to Execution tab**

✓ **Execution Tab Shows**:
  - Phase analysis
  - Process tree with all workers
  - Deadlock analysis (should be CLEAN)

✓ **Intelligence Tab Shows** (after ~2 seconds):
  - Anomaly Timeline (should show activity from 0-30s)
  - Threat Classification: **ANOMALOUS**
  - Threat Type: **CRYPTO_MINING**
  - Anomaly Alerts with evidence

### ✅ Success Criteria
- [ ] CPU reaches 80%+
- [ ] Graphs stop updating after Stop clicked
- [ ] Charts remain visible (not cleared)
- [ ] Can scroll graphs left to see earlier data
- [ ] Anomaly detected as CRYPTO_MINING
- [ ] No false deadlock alerts

---

## 🧪 Test 2: Memory Leak Simulation

### What to Test
Memory leak detection with rising memory usage pattern

### Procedure

**Step 1: Start Profiling**
- Program Path: `backend/simulations/memory_leak.py`
- Duration: 45 seconds
- Click "Profile Now"

**Step 2: Observe Memory Growth**
✓ CPU stays low (5-10%)
✓ Memory rises continuously
✓ Charts update in real-time

**Step 3: After Stop**
✓ Graphs persist showing memory growth trajectory
✓ Scroll left to see full growth from 0-45s
✓ Intelligence tab shows MEMORY_LEAK anomaly

### Expected Output
```
Program Resource Usage Chart:
- CPU: Flat line around 8%
- Memory: Diagonal line rising from 12% to 45%
- Time: 0:00 to 0:45
```

### ✅ Success Criteria
- [ ] Memory rises steadily
- [ ] CPU remains low
- [ ] Graph shows clear upward memory trend
- [ ] Anomaly type: MEMORY_LEAK
- [ ] Charts persist after Stop

---

## 🧪 Test 3: Deadlock Simulation

### What to Test
Deadlock detection with wait-for graph visualization

### Procedure

**Step 1: Start Profiling**
- Program Path: `backend/simulations/deadlock_sim.py`
- Duration: 30 seconds
- Click "Profile Now"

**Step 2: Observe Execution**
✓ Both CPU and Memory moderate (~20-30%)
✓ See multiple threads waiting
✓ Occasional lock timeout messages in background

**Step 3: After Stop**
✓ Execution tab shows deadlock analysis
✓ **Wait-for Graph** displays with:
  - Thread nodes (circles labeled with thread IDs)
  - Connection lines showing wait-for relationships
  - Cycle highlighting potential deadlock
  
✓ **Deadlock Alerts** shows: "DEADLOCK DETECTED" (or similar)
✓ **Suggested Fixes** provides recommendations

### Expected Output
```
Concurrency Analysis Section:
├─ Wait-for Graph: [Interactive D3.js graph with 2 nodes and cycle]
├─ Deadlock Alerts: ⚠ DEADLOCK DETECTED
├─ Suggested Fixes: Lock ordering, timeout mechanisms
└─ Deadlock History: Timestamp of detected cycles
```

### ✅ Success Criteria
- [ ] Wait-for graph renders with visible nodes
- [ ] Graph shows circular cycle (deadlock evidence)
- [ ] Deadlock alerts populated
- [ ] Risk level shows MEDIUM or HIGH
- [ ] Suggested fixes appear
- [ ] No JavaScript errors in console

---

## 🎨 Test 4: Graph Persistence & Scrolling

### What to Test
Graphs stop updating and remain scrollable after profiling

### Procedure

**Step 1: Run Long Profiling (90+ seconds)**
- Use crypto_miner.py
- Duration: 90 seconds
- Click "Profile Now"

**Step 2: Wait 30 seconds**
✓ Charts update normally
✓ Data point added every ~1 second
✓ See 30 data points

**Step 3: Click Stop**
✓ Charts immediately stop updating
✓ **No new data points appear** (test this for 5-10 seconds)
✓ All 90 datapoints remain on chart

**Step 4: Scroll Left**
✓ Position mouse over **Program Resource Usage** chart
✓ Use horizontal scroll bar or mousewheel
✓ See earlier time periods (0:00 - 1:00)
✓ Can scroll right to see most recent data

### ✅ Success Criteria
- [ ] New data STOPS being added after Stop clicked
- [ ] No chart update for 10+ seconds after Stop
- [ ] Full timeline remains visible
- [ ] Can scroll horizontally to view all data
- [ ] Scroll position remembered within tab

---

## 🎬 Test 5: Combined Anomalies

### What to Test
Multiple simultaneous anomalies detected together

### Procedure

**Step 1: Start Multiple Simulations in Background**
```bash
# Terminal 1
python app.py

# Terminal 2 - Run all three together
cd backend/simulations
python crypto_miner.py 60 &
python memory_leak.py 60 &
python deadlock_sim.py 60 &
```

**Step 2: Profile the Combined Load**
- Program Path: `backend/simulations/crypto_miner.py`
- Duration: 60 seconds
- Click "Profile Now"

**Step 3: Observe Concurrent Anomalies**
✓ CPU high (from crypto_miner)
✓ Memory rising (from memory_leak)
✓ Multiple threads detected
✓ Lock contention visible

**Step 4: After Stop**
✓ Intelligence tab shows:
  - Multiple anomaly types: CRYPTO_MINING, MEMORY_LEAK
  - Combined threat level: HIGH
  - Timeline showing all activities
  - Process relationships

### Expected Output
```
Intelligence Tab:
- Threat Classification: ANOMALOUS (High risk)
- Detected Anomalies:
  ✓ CRYPTO_MINING (84% CPU)
  ✓ MEMORY_LEAK (rising 2% per second)
  ✓ DEADLOCK (potential lock cycles)
- Recommendations: Inspect all processes, kill malicious ones
```

### ✅ Success Criteria
- [ ] Multiple anomalies detected
- [ ] Threat level HIGH
- [ ] Each anomaly correctly classified
- [ ] Combined risk assessment accurate
- [ ] Recommendations provided

---

## 🔍 Debugging & Troubleshooting

### Issue: Graphs Still Updating After Stop
**Cause**: `profilingInProgress` flag not set or `stopRealTimeUpdates()` not called

**Solution**:
```javascript
// Check in browser console (F12):
profilingInProgress  // Should show: false after Stop clicked
realtimeUpdateInterval  // Should show: null after Stop clicked
```

**Fix**: Check that Stop button handler includes:
```javascript
profilingInProgress = false;
stopRealTimeUpdates();
```

### Issue: Deadlock Graph Not Rendering
**Cause**: D3.js library not loaded or data not returned

**Solution**:
```javascript
// In browser console:
d3  // Should show: Object (d3.js loaded)
// Try fetching deadlock data manually:
fetch('/api/profile/1234/deadlock').then(r => r.json()).then(d => console.log(d))
```

### Issue: Anomaly Not Detected
**Cause**: Model files missing or simulation too short

**Solution**:
- Verify `backend/models/` contains `.pkl` files
- Run simulation for at least 20 seconds
- Check console for model loading warnings

### Issue: Simulations Won't Start
**Cause**: Python issues or missing imports

**Solution**:
```bash
# Test individual simulation
python backend/simulations/crypto_miner.py 10

# Should print: [Crypto Miner] Starting...
# Watch for: [Crypto Worker X] Started messages
```

---

## 📊 Expected Performance

| Simulation | CPU | Memory | Duration | Anomaly Type |
|-----------|-----|--------|----------|--------------|
| crypto_miner.py | 80-95% | 5-10% stable | 30-60s ⭐ | CRYPTO_MINING |
| memory_leak.py | 5-10% | Rises to 50%+ | 45-90s ⭐ | MEMORY_LEAK |
| deadlock_sim.py | 20-30% | 15-25% stable | 30-60s ⭐ | DEADLOCK |

⭐ = Recommended duration for best results

---

## 📈 Verification Checklist

### Pre-Testing
- [ ] Flask server running on localhost:5000
- [ ] Browser can access dashboard
- [ ] All 6 simulations exist in `backend/simulations/`
- [ ] Models loaded successfully

### During Testing
- [ ] Crypto miner shows high CPU
- [ ] Memory leak shows rising memory
- [ ] Deadlock shows lock cycles
- [ ] Graphs update in real-time
- [ ] No console errors

### After Stop
- [ ] Graphs stop updating
- [ ] View switches to Execution tab (auto)
- [ ] Anomalies detected and classified
- [ ] Graphs remain visible
- [ ] Can scroll through timeline
- [ ] Results persist until new profile

### Final Verification
- [ ] All 3 anomaly types detected
- [ ] Threat classification accurate
- [ ] Wait-for graph renders for deadlock
- [ ] No false positives
- [ ] Performance meets expectations

---

## 📝 Notes

1. **System Load**: Crypto miner will load your system heavily. Close other apps if needed.

2. **Deadlock Timing**: Deadlock may take 5-10 seconds to manifest. This is normal due to timeout mechanisms.

3. **Memory Leak**: Memory continues growing until program dies. Monitor closely on constrained systems.

4. **Graph Scrolling**: Enable horizontal scrollbar in chart area for better UX. Can use mouse wheel left/right.

5. **Thread Safety**: All simulations use thread-safe operations. Safe to run concurrently.

---

## 🚀 Next Steps

After successful testing:

1. **Create Custom Simulations**: Use these as templates
2. **Test on Different Systems**: Windows, Linux, macOS
3. **Tune Detection Thresholds**: Adjust anomaly detection sensitivity
4. **Benchmark Performance**: Measure profiler overhead
5. **Production Deployment**: Use verified configurations

---

**Everything Ready! Start Testing! 🎉**

```bash
# Quick start command
cd c:\Users\SATYA ADITYA INFRA\OS_EL\backend
python app.py
# Then open http://localhost:5000
```

---

**Last Updated**: 2026-02-09  
**Test Status**: ✅ Ready  
**Simulations Status**: ✅ 6 Available (3 New)  
**Graph Persistence**: ✅ Implemented  

