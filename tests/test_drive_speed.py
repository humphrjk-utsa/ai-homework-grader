#!/usr/bin/env python3
"""
Test external drive speed and Ollama model loading performance
"""

import time
import requests
import subprocess
import os
import tempfile

def test_drive_speed():
    """Test read/write speed of the current directory (external drive)"""
    print("🔍 Testing drive speed...")
    
    # Test write speed
    test_file = "speed_test.tmp"
    test_size_mb = 100  # 100MB test file
    
    try:
        print(f"📝 Writing {test_size_mb}MB test file...")
        start_time = time.time()
        
        with open(test_file, 'wb') as f:
            # Write 100MB of data
            chunk = b'0' * (1024 * 1024)  # 1MB chunks
            for i in range(test_size_mb):
                f.write(chunk)
        
        write_time = time.time() - start_time
        write_speed = test_size_mb / write_time
        
        print(f"✅ Write speed: {write_speed:.1f} MB/s")
        
        # Test read speed
        print(f"📖 Reading {test_size_mb}MB test file...")
        start_time = time.time()
        
        with open(test_file, 'rb') as f:
            data = f.read()
        
        read_time = time.time() - start_time
        read_speed = test_size_mb / read_time
        
        print(f"✅ Read speed: {read_speed:.1f} MB/s")
        
        # Clean up
        os.remove(test_file)
        
        return read_speed, write_speed
        
    except Exception as e:
        print(f"❌ Drive speed test failed: {e}")
        return None, None

def test_ollama_model_loading():
    """Test actual Ollama model loading time"""
    print("\n🤖 Testing Ollama model loading...")
    
    try:
        # Check if model is currently loaded
        response = requests.get("http://localhost:11434/api/ps", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            gpt_loaded = any("gpt-oss:120b" in m.get("name", "") for m in models)
            
            if gpt_loaded:
                print("✅ gpt-oss:120b is already loaded in memory")
                return 0
            else:
                print("📥 gpt-oss:120b not loaded, testing load time...")
        
        # Test model loading with a simple request
        start_time = time.time()
        
        payload = {
            "model": "gpt-oss:120b",
            "prompt": "Hello",
            "stream": False,
            "options": {
                "num_predict": 1
            }
        }
        
        print("⏱️  Sending request to load model...")
        response = requests.post("http://localhost:11434/api/generate", 
                               json=payload, timeout=300)
        
        load_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Model loaded successfully in {load_time:.1f} seconds")
            
            # Calculate effective transfer rate
            model_size_gb = 65.3  # gpt-oss:120b is ~65GB
            effective_rate = model_size_gb / load_time
            print(f"📊 Effective model loading rate: {effective_rate:.2f} GB/s")
            
            return load_time
        else:
            print(f"❌ Model loading failed: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("⏰ Model loading timed out (>5 minutes)")
        return None
    except Exception as e:
        print(f"❌ Model loading test failed: {e}")
        return None

def check_system_info():
    """Check system and storage information"""
    print("💻 System Information:")
    
    try:
        # Check available memory
        result = subprocess.run(['sysctl', 'hw.memsize'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            mem_bytes = int(result.stdout.split(':')[1].strip())
            mem_gb = mem_bytes / (1024**3)
            print(f"📊 Total RAM: {mem_gb:.0f} GB")
    except:
        pass
    
    try:
        # Check current directory filesystem
        result = subprocess.run(['df', '-h', '.'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                filesystem = parts[0]
                size = parts[1]
                used = parts[2]
                available = parts[3]
                print(f"💾 Current drive: {filesystem}")
                print(f"📏 Size: {size}, Used: {used}, Available: {available}")
    except:
        pass

def main():
    """Run all performance tests"""
    print("🚀 External Drive & Model Loading Performance Test")
    print("=" * 50)
    
    # System info
    check_system_info()
    print()
    
    # Drive speed test
    read_speed, write_speed = test_drive_speed()
    
    # Model loading test
    load_time = test_ollama_model_loading()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Performance Summary:")
    
    if read_speed:
        print(f"📖 Drive read speed: {read_speed:.1f} MB/s ({read_speed/1000:.2f} GB/s)")
    
    if write_speed:
        print(f"📝 Drive write speed: {write_speed:.1f} MB/s ({write_speed/1000:.2f} GB/s)")
    
    if load_time:
        print(f"🤖 Model load time: {load_time:.1f} seconds")
        
        # Recommendations based on results
        if load_time < 60:
            print("✅ Excellent model loading performance!")
        elif load_time < 120:
            print("👍 Good model loading performance")
        else:
            print("⚠️  Model loading slower than expected")
            print("💡 Consider checking:")
            print("   - External drive connection (USB 3.0+ or Thunderbolt)")
            print("   - Available system memory")
            print("   - Other running applications")

if __name__ == "__main__":
    main()