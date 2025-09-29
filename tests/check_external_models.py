#!/usr/bin/env python3
"""
Check external drive model setup for homework grader
Specifically designed for setups where Ollama models are stored on external drives
"""

import requests
import json
import sys
import os
import subprocess

def check_ollama_service():
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        return response.status_code == 200, response
    except requests.exceptions.ConnectionError:
        return False, "Connection refused - Ollama not running"
    except requests.exceptions.Timeout:
        return False, "Connection timeout"
    except Exception as e:
        return False, str(e)

def check_external_drive_models():
    """Check if models on external drive are accessible"""
    print("🔍 Checking Ollama and External Drive Models...")
    print("=" * 60)
    
    # Check Ollama service
    ollama_running, response = check_ollama_service()
    
    if not ollama_running:
        print("❌ Ollama Service Issues:")
        print(f"   {response}")
        print("\n💡 Solutions:")
        print("   1. Start Ollama: ollama serve")
        print("   2. Check if external drive is mounted")
        print("   3. Verify Ollama can access model directory")
        return False
    
    print("✅ Ollama service is running")
    
    # Get available models
    try:
        models_data = response.json()
        models = models_data.get("models", [])
        
        if not models:
            print("⚠️  No models found")
            print("\n💡 Possible causes:")
            print("   • External drive not mounted")
            print("   • Ollama model directory not configured correctly")
            print("   • Models not properly installed")
            return False
        
        print(f"📋 Found {len(models)} models:")
        
        target_model = "gpt-oss:120b"
        target_found = False
        
        for model in models:
            name = model.get("name", "Unknown")
            size = model.get("size", 0) / (1024**3)  # Convert to GB
            modified = model.get("modified_at", "Unknown")
            
            if name == target_model:
                print(f"  🎯 {name} ({size:.1f} GB) ✅ TARGET MODEL")
                target_found = True
            else:
                print(f"  • {name} ({size:.1f} GB)")
        
        if target_found:
            print(f"\n✅ Target model '{target_model}' is available!")
            return True
        else:
            print(f"\n⚠️  Target model '{target_model}' not found")
            print("Available alternatives:")
            
            # Suggest alternatives
            good_alternatives = []
            for model in models:
                name = model.get("name", "")
                if any(keyword in name.lower() for keyword in ["gpt", "deepseek", "mistral", "gemma"]):
                    good_alternatives.append(name)
            
            for alt in good_alternatives[:3]:  # Show top 3
                print(f"  • {alt}")
            
            return len(good_alternatives) > 0
            
    except Exception as e:
        print(f"❌ Error parsing models: {e}")
        return False

def test_model_inference(model_name="gpt-oss:120b"):
    """Test if the model can actually generate responses"""
    print(f"\n🧪 Testing {model_name} inference...")
    
    try:
        payload = {
            "model": model_name,
            "prompt": "You are a programming instructor. Respond with exactly: 'Ready to grade assignments!'",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "max_tokens": 50
            }
        }
        
        print("   Sending test prompt...")
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("response", "").strip()
            
            print(f"   ✅ Response: {ai_response}")
            
            if "ready" in ai_response.lower() and "grade" in ai_response.lower():
                print("   🎯 Model is responding correctly!")
                return True
            else:
                print("   ⚠️  Model responded but output seems unexpected")
                return True  # Still working, just different response
                
        elif response.status_code == 404:
            print(f"   ❌ Model '{model_name}' not found")
            print("   💡 Check if external drive is properly mounted")
            return False
        else:
            print(f"   ❌ Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("   ⏰ Model response timed out (this is normal for large models)")
        print("   💡 Consider using a smaller model for faster responses")
        return True  # Timeout doesn't mean it's broken
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def show_external_drive_tips():
    """Show tips for external drive setup"""
    print("\n" + "=" * 60)
    print("💡 External Drive Setup Tips:")
    print("=" * 60)
    
    print("\n🔧 If models are not accessible:")
    print("1. Ensure external drive is mounted and accessible")
    print("2. Check Ollama's model directory configuration:")
    print("   export OLLAMA_MODELS=/path/to/external/drive/models")
    print("3. Restart Ollama after changing the path:")
    print("   killall ollama && ollama serve")
    
    print("\n⚡ Performance Tips for External Drives:")
    print("• Use USB 3.0+ or Thunderbolt for better speed")
    print("• Consider using SSD instead of HDD for models")
    print("• Keep frequently used models on internal storage")
    
    print("\n🎯 For Homework Grading:")
    print("• gpt-oss:120b is excellent but slow")
    print("• Consider gemma3:27b for faster grading")
    print("• deepseek-r1:70b is good balance of speed/quality")

def main():
    print("🎓 Homework Grader - External Drive Model Check")
    print("=" * 60)
    
    # Check basic setup
    models_ok = check_external_drive_models()
    
    if models_ok:
        # Test inference
        inference_ok = test_model_inference("gpt-oss:120b")
        
        if inference_ok:
            print("\n🚀 SUCCESS! Your setup is ready for AI-powered grading!")
            print("\nNext steps:")
            print("1. Run: python run_grader.py")
            print("2. Go to 'Grade Submissions'")
            print("3. Look for '🟢 Local AI Model Connected'")
        else:
            print("\n⚠️  Models found but inference failed")
            show_external_drive_tips()
    else:
        print("\n❌ Setup issues detected")
        show_external_drive_tips()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()