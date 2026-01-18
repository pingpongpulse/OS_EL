"""
PhaseSentinel - Build Verification Script
Checks that all required files are in place and properly configured
"""

import os
import sys
from pathlib import Path

def check_file(path, file_type="file"):
    """Check if a file or directory exists"""
    if os.path.exists(path):
        print(f"✓ {file_type}: {path}")
        return True
    else:
        print(f"✗ MISSING {file_type}: {path}")
        return False

def check_files_in_dir(directory, file_list):
    """Check if all files exist in a directory"""
    results = []
    for file in file_list:
        path = os.path.join(directory, file)
        results.append(check_file(path))
    return all(results)

def main():
    print("=" * 60)
    print("PhaseSentinel Build Verification")
    print("=" * 60)
    print()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, 'backend')
    frontend_dir = os.path.join(base_dir, 'frontend')
    
    all_good = True
    
    # Check backend Python files
    print("📦 Backend Python Modules:")
    backend_files = [
        'app.py',
        'phaseprofiler.py',
        'deadlock_detector.py',
        'anomaly_detector.py',
        'recommender.py',
        'requirements.txt'
    ]
    for file in backend_files:
        if not check_file(os.path.join(backend_dir, file)):
            all_good = False
    
    print()
    
    # Check frontend templates
    print("🎨 Frontend HTML Templates:")
    template_files = [
        os.path.join(frontend_dir, 'templates', 'index.html'),
        os.path.join(frontend_dir, 'templates', 'dashboard.html'),
        os.path.join(frontend_dir, 'templates', 'results.html')
    ]
    for file in template_files:
        if not check_file(file):
            all_good = False
    
    print()
    
    # Check static assets
    print("🎯 Static Assets (CSS/JS):")
    static_files = [
        os.path.join(frontend_dir, 'static', 'css', 'style.css'),
        os.path.join(frontend_dir, 'static', 'js', 'charts.js')
    ]
    for file in static_files:
        if not check_file(file):
            all_good = False
    
    print()
    
    # Check directories
    print("📁 Required Directories:")
    dirs = [
        os.path.join(backend_dir, 'models'),
        os.path.join(backend_dir, 'data')
    ]
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory exists: {directory}")
    
    print()
    print("=" * 60)
    
    if all_good:
        print("✅ All files present and ready to run!")
        print()
        print("Next steps:")
        print("  1. cd backend")
        print("  2. pip install -r requirements.txt")
        print("  3. python app.py")
        print("  4. Open http://localhost:5000 in your browser")
    else:
        print("❌ Some files are missing. Please check the output above.")
        sys.exit(1)
    
    print("=" * 60)

if __name__ == '__main__':
    main()
