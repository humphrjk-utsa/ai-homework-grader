#!/usr/bin/env python3
"""Simple script to restart Streamlit"""

import subprocess
import time
import sys

print("🔄 Restarting Streamlit...")

# Kill existing Streamlit
print("Stopping Streamlit...")
try:
    subprocess.run(["pkill", "-f", "streamlit"], check=False)
    time.sleep(2)
    print("✅ Stopped")
except Exception as e:
    print(f"⚠️ Error stopping: {e}")

# Start Streamlit
print("\nStarting Streamlit...")
try:
    # Start in background
    subprocess.Popen(
        ["streamlit", "run", "app.py", "--server.port", "8501"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    print("✅ Started")
    time.sleep(3)
    
    # Check if it's running
    result = subprocess.run(
        ["curl", "-s", "http://localhost:8501"],
        capture_output=True,
        timeout=5
    )
    
    if result.returncode == 0:
        print("\n✅ Streamlit is running on http://localhost:8501")
        print("\n🎉 Ready to grade with new fixes!")
    else:
        print("\n⚠️ Streamlit may still be starting...")
        print("Check http://localhost:8501 in a moment")
        
except Exception as e:
    print(f"❌ Error starting: {e}")
    sys.exit(1)
