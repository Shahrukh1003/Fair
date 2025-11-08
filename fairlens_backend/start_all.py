"""
Startup script to run both Flask API and Streamlit dashboard.

This script starts:
1. Flask API on port 8000 (background)
2. Streamlit dashboard on port 5000 (foreground/webview)
"""

import subprocess
import sys
import time
import os

def main():
    print("=" * 60)
    print("Starting FairLens Fairness Drift Alert System")
    print("=" * 60)
    print()
    
    print("Starting Flask API on port 8000...")
    flask_env = os.environ.copy()
    flask_env['FLASK_PORT'] = '8000'
    
    flask_process = subprocess.Popen(
        [sys.executable, 'fairlens_backend/app.py'],
        env=flask_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    time.sleep(3)
    print("Flask API started (background)")
    print()
    
    print("Starting Streamlit Dashboard on port 5000...")
    print("Access the dashboard at http://127.0.0.1:5000")
    print("=" * 60)
    print()
    
    streamlit_process = subprocess.Popen(
        [sys.executable, '-m', 'streamlit', 'run',
         'fairlens_backend/dashboard.py',
         '--server.port', '5000',
         '--server.address', '0.0.0.0']
    )
    
    try:
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        flask_process.terminate()
        streamlit_process.terminate()
        print("FairLens services stopped")

if __name__ == '__main__':
    main()
