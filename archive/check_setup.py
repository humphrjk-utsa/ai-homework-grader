#!/usr/bin/env python3
"""
Setup Checker for Homework Grader
Verifies all dependencies and configurations are ready
"""

import sys
import subprocess
import importlib
import requests
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version:", f"{version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print("❌ Python 3.8+ required, found:", f"{version.major}.{version.minor}.{version.micro}")
        return False

def check_required_packages():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit', 'pandas', 'numpy', 'scikit-learn', 
        'nbformat', 'nbconvert', 'requests', 'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            missing_packages.append(package)
    
    return missing_packages

def check_ollama_connection():
    """Check if Ollama is running and accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("✅ Ollama is running")
            
            # Check for gpt-oss model
            gpt_models = [m for m in models if "gpt-oss" in m.get("name", "")]
            if gpt_models:
                print(f"✅ Found gpt-oss model: {gpt_models[0]['name']}")
            else:
                print("⚠️  gpt-oss:120b model not found")
                print("   Run: ollama pull gpt-oss:120b")
            
            return True
        else:
            print("❌ Ollama responded with error:", response.status_code)
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama (http://localhost:11434)")
        print("   Make sure Ollama is installed and running")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def check_directories():
    """Check if required directories exist"""
    required_dirs = [
        "assignments", "submissions", "feedback_reports", 
        "models", "templates", "docs", "tests", "scripts"
    ]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/ directory")
        else:
            print(f"⚠️  {dir_name}/ directory missing (will be created)")
            dir_path.mkdir(exist_ok=True)

def main():
    """Run all setup checks"""
    print("🔍 Homework Grader Setup Check")
    print("=" * 40)
    
    all_good = True
    
    # Check Python version
    print("\n📍 Python Version:")
    if not check_python_version():
        all_good = False
    
    # Check packages
    print("\n📦 Required Packages:")
    missing = check_required_packages()
    if missing:
        all_good = False
        print(f"\n💡 Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
    
    # Check Ollama
    print("\n🤖 AI Model (Ollama):")
    if not check_ollama_connection():
        all_good = False
    
    # Check directories
    print("\n📁 Directory Structure:")
    check_directories()
    
    # Final status
    print("\n" + "=" * 40)
    if all_good:
        print("🎉 Setup complete! Ready to run homework grader.")
        print("🚀 Start with: python start.py")
    else:
        print("⚠️  Setup issues found. Please resolve them before starting.")
    
    return all_good

if __name__ == "__main__":
    main()