#!/usr/bin/env python3
"""
Test script to verify local AI model connection
Run this to check if OS120 or other models are properly configured
"""

import requests
import json
import sys

def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("✅ Ollama is running!")
            print(f"📋 Available models: {len(models)}")
            
            for model in models:
                name = model.get("name", "Unknown")
                size = model.get("size", 0) / (1024**3)  # Convert to GB
                print(f"  • {name} ({size:.1f} GB)")
            
            return True, models
        else:
            print("❌ Ollama is running but returned error")
            return False, []
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama")
        print("💡 Make sure Ollama is running: ollama serve")
        return False, []
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        return False, []

def test_model_response(model_name="OS120"):
    """Test if a specific model can generate responses"""
    try:
        payload = {
            "model": model_name,
            "prompt": "Hello! Can you help me grade programming assignments? Please respond with 'Yes, I can help with grading.'",
            "stream": False,
            "options": {
                "temperature": 0.3,
                "max_tokens": 100
            }
        }
        
        print(f"🧪 Testing {model_name} model...")
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("response", "")
            
            print(f"✅ {model_name} is working!")
            print(f"📝 Response: {ai_response[:100]}...")
            return True
        else:
            print(f"❌ {model_name} returned error: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏰ {model_name} response timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing {model_name}: {e}")
        return False

def main():
    print("🔍 Testing Local AI Model Connection")
    print("=" * 50)
    
    # Test Ollama connection
    ollama_working, models = test_ollama_connection()
    
    if not ollama_working:
        print("\n💡 Setup Instructions:")
        print("1. Install Ollama: https://ollama.ai/download")
        print("2. Start Ollama: ollama serve")
        print("3. Install OS120: ollama pull OS120")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Test your preferred model first
    models_to_test = [
        "gpt-oss:120b",              # Your preferred model
        "deepseek-r1:70b",
        "mistral-small3.1:24b-instruct-2503-q8_0", 
        "gemma3:27b"
    ]
    
    available_model_names = [m.get("name", "") for m in models]
    working_models = []
    
    for model_name in models_to_test:
        if model_name in available_model_names:
            if test_model_response(model_name):
                working_models.append(model_name)
        else:
            print(f"⚠️  {model_name} not found in your models")
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    
    if working_models:
        print(f"✅ {len(working_models)} working model(s):")
        for model in working_models:
            print(f"  • {model}")
        
        print(f"\n🎯 Recommended: Use {working_models[0]} for homework grading")
        print("🚀 Your homework grader is ready to use local AI!")
        
    else:
        print("❌ No working models found")
        print("\n💡 Quick Setup:")
        print("ollama pull OS120")
        print("# Wait for download, then run this test again")
    
    print("\n🔧 To use in homework grader:")
    print("1. Start your grader: python run_grader.py")
    print("2. Go to 'Grade Submissions'")
    print("3. Look for '🟢 Local AI Model Connected'")

if __name__ == "__main__":
    main()