# PhaseSentinel Quick Start

Welcome to PhaseSentinel! This guide will get you up and running in under 5 minutes.

## 🎯 What is PhaseSentinel?

PhaseSentinel is an **AI-powered program profiler** that:
- Monitors your system in real-time
- Detects CPU/memory/I/O bottlenecks
- Analyzes deadlock risks
- Recommends optimizations with predicted speedup
- Provides a beautiful web dashboard

## ⚡ 30-Second Start

**Windows:**
```bash
cd c:\PROJECTS\OS_EL
start.bat
```

**macOS/Linux:**
```bash
cd /path/to/OS_EL
chmod +x start.sh
./start.sh
```
http://localhost:5000
Then open: **** in your browser
## 📖 First Steps

### 1. View the Dashboard
- Open the app in your browser
- Click "Dashboard" in the navigation bar
- See sample metrics with real-time charts

### 2. Start a Profile
- Click the "Start Profiling" button
- Set duration (1-300 seconds)
- Watch the profiler collect metrics
- View results automatically

### 3. Analyze Results
- See detected bottlenecks
- Review anomaly alerts
- Read optimization suggestions
- Check predicted speedup

## 🔧 Setup Verification

Run this to verify everything is installed correctly:

```bash
python verify_build.py
```

You should see:
```
✅ All files present and ready to run!
```

## 🎨 Features You'll See

### Real-time Metrics
- CPU usage timeline
- Memory usage timeline
- Phase distribution (pie chart)

### Bottleneck Detection
- CPU-bound phases (>70% usage)
- Memory-bound phases (rapid growth)
- I/O-bound phases (high wait times)
- Severity labels (high/medium/low)

### Smart Recommendations
- Phase-specific optimization strategies
- Predicted speedup improvements
- Actionable next steps

## 📊 API Examples

Test the API with curl:

```bash
# Start a 5-second profile
curl -X POST http://localhost:5000/api/profile \
  -H "Content-Type: application/json" \
  -d '{"duration": 5}'

# Get health status
curl http://localhost:5000/api/health
```

## 🤔 FAQ

**Q: Do I need to install ML models?**
A: No! The app works perfectly without models. Models are optional for enhanced features.

**Q: What if the app crashes?**
A: It won't! It has comprehensive error handling. If something fails, check the terminal output.

**Q: Can I change the profiling duration?**
A: Yes! Durations can be 1-300 seconds. Start with 10 seconds for testing.

**Q: Will this slow down my system?**
A: No. Profiling uses <1% CPU overhead.

## 📚 Learn More

- **Full Setup Guide:** `SETUP_GUIDE.md`
- **Complete Documentation:** `PHASESNOEL_README.md`
- **Build Summary:** `BUILD_SUMMARY.md`

## ⚙️ Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID [PID] /F

# macOS/Linux
lsof -i :5000
kill -9 [PID]
```

### Missing Dependencies
```bash
cd backend
pip install --force-reinstall -r requirements.txt
```

### Templates Not Found
```bash
# Ensure you're in the project root
cd c:\PROJECTS\OS_EL
```

## 🚀 What's Next?

1. **Profile your program** - Click "Start Profiling" to begin
2. **View results** - See bottlenecks and recommendations
3. **Export data** - Download results as JSON
4. **Add models** (optional) - Train ML models for better predictions
5. **Deploy** - Use Gunicorn for production

## 💡 Pro Tips

- **Quick Profile:** Click the quick-start button on the home page
- **Sample Data:** Click "Load Sample Data" on the dashboard
- **Export Results:** Click "Export" to download analysis as JSON
- **Monitor Over Time:** Run multiple profiles to track improvements

## 📞 Need Help?

1. Check the **Troubleshooting** section above
2. Review **SETUP_GUIDE.md** for detailed instructions
3. Look at **PHASESNOEL_README.md** for full documentation

---

**You're all set! Open http://localhost:5000 and start profiling! ⚡**

For more information, see the `PHASESNOEL_README.md` file.
