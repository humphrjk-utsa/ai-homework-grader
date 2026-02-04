#!/usr/bin/env python3
"""
Test Ollama Setup for Homework Grader
"""

import requests
import json

def test_ollama_connection():
    """Test Ollama connection"""
    print("🔍 Testing Ollama connection...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running")
            return True
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return False

def list_available_models():
    """List available Ollama models"""
    print("\n📋 Available Ollama Models:")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            
            # Categorize models
            code_models = []
            feedback_models = []
            other_models = []
            
            for model in models:
                name = model["name"]
                size_gb = model.get("size", 0) / (1024**3)
                
                if any(keyword in name.lower() for keyword in ["qwen", "coder", "deepseek"]):
                    code_models.append((name, size_gb))
                elif any(keyword in name.lower() for keyword in ["gemma", "llama", "mistral"]):
                    feedback_models.append((name, size_gb))
                else:
                    other_models.append((name, size_gb))
            
            print("🔧 Code Analysis Models:")
            for name, size in code_models:
                print(f"   • {name} ({size:.1f}GB)")
            
            print("\n📝 Feedback Generation Models:")
            for name, size in feedback_models:
                print(f"   • {name} ({size:.1f}GB)")
            
            if other_models:
                print("\n🔍 Other Models:")
                for name, size in other_models:
                    print(f"   • {name} ({size:.1f}GB)")
            
            return models
        else:
            print("❌ Failed to get model list")
            return []
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return []

def recommend_model_pairs(models):
    """Recommend optimal model pairs"""
    print("\n💡 Recommended Model Pairs for Homework Grading:")
    print("=" * 60)
    
    # Find best combinations
    qwen_models = [m for m in models if "qwen" in m["name"].lower()]
    gemma_models = [m for m in models if "gemma" in m["name"].lower() and "27b" in m["name"]]
    llama_models = [m for m in models if "llama" in m["name"].lower()]
    
    if qwen_models and gemma_models:
        qwen = qwen_models[0]["name"]  # Take first Qwen model
        gemma = next((m["name"] for m in gemma_models if "q8_0" in m["name"]), gemma_models[0]["name"])
        
        print(f"🎯 OPTIMAL PAIR:")
        print(f"   Code Analysis: {qwen}")
        print(f"   Feedback Generation: {gemma}")
        print(f"   💡 This uses your existing Qwen 3.0 30B + Gemma 3.0 27B Q8_0!")
        
        return qwen, gemma
    
    elif qwen_models and llama_models:
        qwen = qwen_models[0]["name"]
        llama = llama_models[0]["name"]
        
        print(f"🎯 ALTERNATIVE PAIR:")
        print(f"   Code Analysis: {qwen}")
        print(f"   Feedback Generation: {llama}")
        
        return qwen, llama
    
    else:
        print("⚠️ No optimal pairs found")
        return None, None

def test_model_response(model_name):
    """Test a quick response from a model"""
    print(f"\n🧪 Testing {model_name}...")
    
    try:
        payload = {
            "model": model_name,
            "prompt": "Hello! Can you help with code analysis?",
            "stream": False,
            "options": {
                "num_predict": 50,
                "temperature": 0.3
            }
        }
        
        response = requests.post("http://localhost:11434/api/generate", 
                               json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get("response", "")
            print(f"✅ {model_name} is working!")
            print(f"📝 Sample response: {generated_text[:100]}...")
            return True
        else:
            print(f"❌ {model_name} failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {model_name} test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Ollama Setup Test for Homework Grader")
    print("=" * 50)
    
    # Test connection
    if not test_ollama_connection():
        print("\n❌ Ollama is not running or not accessible")
        print("💡 Start Ollama and try again")
        return False
    
    # List models
    models = list_available_models()
    
    if not models:
        print("\n❌ No models found in Ollama")
        return False
    
    # Recommend pairs
    code_model, feedback_model = recommend_model_pairs(models)
    
    if code_model and feedback_model:
        print(f"\n🧪 Testing recommended models...")
        
        # Test both models
        code_ok = test_model_response(code_model)
        feedback_ok = test_model_response(feedback_model)
        
        if code_ok and feedback_ok:
            print(f"\n🎉 Ollama setup is ready for homework grading!")
            print(f"💡 Use these models:")
            print(f"   Code Analysis: {code_model}")
            print(f"   Feedback Generation: {feedback_model}")
            print(f"\n💡 Next steps:")
            print(f"   1. Run: streamlit run pc_start.py")
            print(f"   2. Select 'Ollama' as backend")
            print(f"   3. Start grading!")
            return True
        else:
            print(f"\n⚠️ Some models are not responding properly")
            return False
    else:
        print(f"\n⚠️ Could not find suitable model pairs")
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)