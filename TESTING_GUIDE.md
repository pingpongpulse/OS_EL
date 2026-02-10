# Quick Testing Guide - Stop Button & Deadlock Display

## How to Test the Changes

### Prerequisites
```bash
# Navigate to project
cd c:\Users\SATYA ADITYA INFRA\OS_EL

# Install dependencies (if not done)
cd backend
pip install -r requirements.txt
cd ..

# Start Flask server
cd backend
python app.py
```

Server should start on `http://localhost:5000`

---

## Step-by-Step Test Procedure

### 1. Open Dashboard
- Navigate to `http://localhost:5000` in your browser
- You should see the "Overview" tab active

### 2. Start Profiling
- Click the **"Start Profiling"** button
- Set a duration: **10 seconds** (for quick testing)
- Click **"Profile Now"**
- Observe the **"Stop"** button appears (red button)
- Watch metrics collect in the Overview tab

### 3. Click Stop Button
Choose ONE of:
- **Option A:** Wait for 10 seconds (auto-stops) 
- **Option B:** Manually click the **"Stop"** button

Expected behavior:
- ✓ Status changes to "Stopped"
- ✓ Stop button disappears  
- ✓ Timer hides
- ✓ **View automatically switches to "Execution & Concurrency Analysis" tab**

### 4. Verify Concurrency Analysis Section
You should now see the **"Concurrency Analysis"** card with:

#### Subsection 1: Wait-for Graph
- [x] **If no deadlock detected:**
  ```
  "Wait-for graph displays only when deadlock cycles are detected"
  ```
  
- [x] **If deadlock detected:**
  - Visual graph with interactive nodes
  - Draggable thread circles
  - Connection lines showing wait-for relationships
  - Color-coded thread nodes

#### Subsection 2: Deadlock Alerts
- [x] **If no deadlock:**
  ```
  ✓ No Deadlocks Detected
  Risk Level: LOW
  3 locks currently tracked
  ```
  
- [x] **If deadlock:**
  ```
  ⚠ DEADLOCK DETECTED!
  [X] cycle(s) found
  Risk Level: [HIGH/MEDIUM]
  [N] nodes involved
  ```

#### Subsection 3: Suggested Fixes
- [x] **General best practices** for normal operation
- [x] **Specific fixes** for deadlock scenarios
  - Implement lock ordering protocol
  - Use timeout-based locks
  - Consider lock-free algorithms
  - Review thread synchronization patterns

#### Subsection 4: Deadlock History
- [x] Shows historical deadlock records (if any)
- [x] Shows message: "No deadlocks recorded" (normal case)

---

## Expected Results

### Successful Test Output

```
═══════════════════════════════════════════════════════════════
EXECUTION & CONCURRENCY ANALYSIS TAB
═══════════════════════════════════════════════════════════════

Concurrency Analysis
─────────────────────

Wait-for Graph
[Graph area or placeholder message visible]

Deadlock Alerts
✓ No Deadlocks Detected
Risk Level: LOW
3 locks currently tracked

Suggested Fixes
• Maintain consistent lock ordering
• Use RAII for lock management
• Monitor lock contention regularly
• Consider async alternatives when possible

Deadlock History
No deadlock history recorded

═══════════════════════════════════════════════════════════════
```

### What Changed (User-Facing)

| Feature | Before | After |
|---------|--------|-------|
| Stop Button | Stops profiling, shows averages in Overview | Stops profiling, shows averages, **automatically switches to Execution tab, displays full deadlock analysis** |
| Concurrency Tab | Required manual switch | **Auto-switches on Stop** |
| Wait-for Graph | Showed placeholder | **Shows interactive D3.js graph when deadlock detected, placeholder otherwise** |
| Deadlock Alerts | "Monitoring for deadlock risks..." (stuck) | **Actual analysis results** |
| Suggested Fixes | "No issues detected" (stuck) | **Contextual fixes based on risk level** |
| Deadlock History | "No deadlocks recorded" (stuck) | **Shows actual historical data** |

---

## Troubleshooting

### Issue: Stop button doesn't appear
**Solution:** 
- Make sure "Start Profiling" button was clicked
- Check browser console (F12) for JavaScript errors
- Verify Flask server is running

### Issue: Tab doesn't switch automatically
**Solution:**
- Check browser console for errors
- Verify "Execution & Concurrency Analysis" tab exists
- Manual workaround: Click the tab manually

### Issue: Concurrency Analysis shows "undefined" or errors
**Solution:**
- Check browser console (F12) for JavaScript errors
- Verify backend `/api/profile/<pid>/deadlock` endpoint returns data
- Test endpoint manually: 
  ```bash
  curl http://localhost:5000/api/profile/1234/deadlock
  ```

### Issue: Wait-for graph doesn't render
**Solution:**
- Check if D3.js is loaded: See `<script src="https://d3js.org/d3.v7.min.js"></script>` in page source
- Verify browser console for "renderWaitForGraph" errors
- Check that `deadlockData.nodes` and `deadlockData.edges` exist

---

## Browser Console Debugging

### To check for errors:
1. Press `F12` to open Developer Tools
2. Click **Console** tab
3. Look for red error messages
4. Common errors to watch for:
   - `Cannot read property 'forEach' of undefined`
   - `renderWaitForGraph is not a function`
   - `fetch failed: 404` (endpoint not found)

### To test endpoint manually:

```javascript
// In browser console
fetch('/api/profile/1234/deadlock')
    .then(r => r.json())
    .then(d => {
        console.log('Analysis:', d.analysis);
        console.log('Nodes:', d.nodes);
        console.log('Edges:', d.edges);
    });
```

---

## Key Metrics to Verify

### Process Analysis (Overview Tab - After Stop)
- ✓ Average CPU %
- ✓ Max CPU %
- ✓ Average Memory %
- ✓ Max Memory %
- ✓ Total Samples

### Concurrency Analysis (Execution Tab - After Stop)
- ✓ Wait-for Graph (interactive or placeholder)
- ✓ Deadlock Alerts (actual data)
- ✓ Suggested Fixes (contextual)
- ✓ Deadlock History (if applicable)

---

## Success Criteria

✓ **Test is SUCCESSFUL if:**
1. Stop button hides after clicking
2. View switches to "Execution & Concurrency Analysis" tab
3. All four Concurrency Analysis subsections show actual data
4. Wait-for graph renders when deadlock present OR shows placeholder when not
5. No errors in browser console
6. All sections clearly visible and readable

---

## Performance Notes

- Initial fetch: ~500ms after Stop clicked
- Graph rendering: <1 second for reasonable number of nodes
- Tab switch animation: ~300ms
- Total experience: Should feel responsive (< 2 seconds total)

---

## Next Documentation

- See `FINAL_IMPLEMENTATION_SUMMARY.md` for technical details
- See `QUICKSTART.md` for general setup
- See `PHASESNOEL_README.md` for full documentation

---

**Ready to test? Let's go! 🚀**
