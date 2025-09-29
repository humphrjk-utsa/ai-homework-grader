#!/usr/bin/env python3
"""
Test model loading with detailed diagnostics
"""

import time
import requests
import json

def test_model_loading():
    """Test model loading with detailed timing"""
    print("🔍 Testing gpt-oss:120b loading...")
    
    # Check initial status
    print("📊 Initial status check...")
    try:
        response = requests.get("http://localhost:11434/api/ps", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"   Currently loaded models: {len(models)}")
            for model in models:
                print(f"   - {model.get('name', 'unknown')}")
        else:
            print(f"   Error checking status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test with minimal request
    print("\n🚀 Sending minimal request...")
    start_time = time.time()
    
    payload = {
        "model": "gpt-oss:120b",
        "prompt": "Hi",
        "stream": False,
        "options": {
            "num_predict": 1,
            "temperature": 0.1
        }
    }
    
    try:
        print("   Sending request...")
        response = requests.post("http://localhost:11434/api/generate", 
                               json=payload, timeout=120)  # 2 minute timeout
        
        elapsed = time.time() - start_time
        print(f"   Response received in {elapsed:.1f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success! Response: {result.get('response', 'No response')}")
            
            # Check if model is now loaded
            print("\n📊 Post-request status check...")
            status_response = requests.get("http://localhost:11434/api/ps", timeout=5)
            if status_response.status_code == 200:
                models = status_response.json().get("models", [])
                print(f"   Currently loaded models: {len(models)}")
                for model in models:
                    name = model.get('name', 'unknown')
                    size = model.get('size', 0)
                    size_gb = size / (1024**3) if size > 0 else 0
                    print(f"   - {name} ({size_gb:.1f} GB)")
            
            return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"   ⏰ Timeout after {elapsed:.1f} seconds")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"   ❌ Error after {elapsed:.1f} seconds: {e}")
        return False

def check_ollama_logs():
    """Check recent Ollama logs for errors"""
    print("\n📋 Checking Ollama logs...")
    try:
        import subprocess
        result = subprocess.run(['tail', '-20', '/Volumes/ext2/ai-models/ollama/logs/server.log'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("Recent log entries:")
            for line in result.stdout.strip().split('\n')[-10:]:
                if line.strip():
                    print(f"   {line}")
        else:
            print("   Could not read server logs")
    except Exception as e:
        print(f"   Error reading logs: {e}")

def main():
    """Run diagnostics"""
    print("🔧 Model Loading Diagnostics")
    print("=" * 40)
    
    # Test loading
    success = test_model_loading()
    
    # Check logs if failed
    if not success:
        check_ollama_logs()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Model loading successful!")
    else:
        print("❌ Model loading failed")
        print("\n💡 Possible solutions:")
        print("   1. Restart Ollama: killall ollama && ollama serve")
        print("   2. Check external drive connection")
        print("   3. Try smaller model first: ollama run gpt-oss:20b")
        print("   4. Check available memory: top -l 1 | grep PhysMem")

if __name__ == "__main__":
    main()