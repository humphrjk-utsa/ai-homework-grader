#!/usr/bin/env python3
"""
Homework Grader - Startup Script
Simple launcher for the AI-powered homework grading system
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the homework grading system"""
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🚀 Starting AI-Powered Homework Grader...")
    print("📍 Working directory:", script_dir)
    print("🌐 Opening web interface at: http://localhost:8505")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8505",
            "--server.address", "localhost"
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down homework grader...")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting application: {e}")
        print("💡 Make sure Streamlit is installed: pip install streamlit")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()