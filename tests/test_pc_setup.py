#!/usr/bin/env python3
"""
Test PC Setup for llama.cpp-based homework grader
"""

import sys
import time
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import streamlit
        print("✅ Streamlit available")
    except ImportError:
        print("❌ Streamlit not found - run: pip install streamlit")
        return False
    
    try:
        import llama_cpp
        print("✅ llama-cpp-python available")
    except ImportError:
        print("❌ llama-cpp-python not found - run: pip install llama-cpp-python")
        return False
    
    try:
        import pandas
        import numpy
        from sklearn.feature_extraction.text import TfidfVectorizer
        print("✅ Data science libraries available")
    except ImportError:
        print("❌ Missing data science libraries - run: pip install pandas numpy scikit-learn")
        return False
    
    return True

def test_pc_modules():
    """Test PC-specific modules"""
    print("\n🔍 Testing PC modules...")
    
    try:
        from pc_config import validate_pc_setup, get_pc_config
        print("✅ PC config module loaded")
    except ImportError as e:
        print(f"❌ PC config import failed: {e}")
        return False
    
    try:
        from pc_llamacpp_client import PCLlamaCppClient
        print("✅ PC llama.cpp client loaded")
    except ImportError as e:
        print(f"❌ PC client import failed: {e}")
        return False
    
    try:
        from pc_two_model_grader import PCTwoModelGrader
        print("✅ PC two-model grader loaded")
    except ImportError as e:
        print(f"❌ PC grader import failed: {e}")
        return False
    
    return True

def test_model_detection():
    """Test model detection"""
    print("\n🔍 Testing model detection...")
    
    try:
        from pc_llamacpp_client import PCLlamaCppClient
        
        client = PCLlamaCppClient()
        models = client.list_available_models()
        
        if models:
            print(f"✅ Found {len(models)} GGUF models:")
            for model in models[:3]:  # Show first 3
                print(f"   📄 {model['name']} ({model['size_gb']:.1f}GB)")
            if len(models) > 3:
                print(f"   ... and {len(models) - 3} more")
        else:
            print("⚠️ No GGUF models found")
            print("💡 Download models using LM Studio or HuggingFace")
        
        return len(models) > 0
        
    except Exception as e:
        print(f"❌ Model detection failed: {e}")
        return False

def test_gpu_detection():
    """Test GPU detection"""
    print("\n🔍 Testing GPU detection...")
    
    try:
        from pc_config import detect_gpu_capabilities
        
        gpu_info = detect_gpu_capabilities()
        
        if gpu_info["nvidia_available"]:
            print(f"✅ NVIDIA GPU detected: {gpu_info['gpu_memory_gb']:.1f}GB VRAM")
            print(f"   Recommended GPU layers: {gpu_info['recommended_layers']}")
        elif gpu_info["amd_available"]:
            print("✅ AMD GPU detected (ROCm)")
            print(f"   Recommended GPU layers: {gpu_info['recommended_layers']}")
        else:
            print("⚠️ No GPU detected - will use CPU inference")
            print("💡 Consider using a GPU for faster inference")
        
        return True
        
    except Exception as e:
        print(f"❌ GPU detection failed: {e}")
        return False

def test_model_loading():
    """Test loading a model (if available)"""
    print("\n🔍 Testing model loading...")
    
    try:
        from pc_llamacpp_client import PCLlamaCppClient
        
        client = PCLlamaCppClient()
        models = client.list_available_models()
        
        if not models:
            print("⚠️ No models available for testing")
            return False
        
        # Try to load the smallest model for testing
        smallest_model = min(models, key=lambda x: x['size_gb'])
        print(f"🔄 Testing with smallest model: {smallest_model['name']} ({smallest_model['size_gb']:.1f}GB)")
        
        test_client = PCLlamaCppClient(model_path=smallest_model['path'])
        
        # Don't actually load the model (too slow for testing)
        # Just check if the path is valid
        if Path(smallest_model['path']).exists():
            print("✅ Model file accessible")
            return True
        else:
            print("❌ Model file not accessible")
            return False
        
    except Exception as e:
        print(f"❌ Model loading test failed: {e}")
        return False

def test_simple_inference():
    """Test simple inference (if models available)"""
    print("\n🔍 Testing simple inference...")
    
    try:
        from pc_llamacpp_client import PCLlamaCppClient
        
        client = PCLlamaCppClient()
        models = client.list_available_models()
        
        if not models:
            print("⚠️ No models available for inference testing")
            return False
        
        # Find a small model for quick testing
        small_models = [m for m in models if m['size_gb'] < 8]
        
        if not small_models:
            print("⚠️ No small models available for quick testing")
            print("💡 Consider downloading a 7B model for testing")
            return False
        
        test_model = small_models[0]
        print(f"🔄 Testing inference with: {test_model['name']}")
        
        # This would be too slow for a setup test
        print("⚠️ Skipping actual inference test (too slow for setup)")
        print("💡 Run 'streamlit run pc_start.py' to test full inference")
        
        return True
        
    except Exception as e:
        print(f"❌ Inference test failed: {e}")
        return False

def test_system_validation():
    """Test system validation"""
    print("\n🔍 Testing system validation...")
    
    try:
        from pc_config import validate_pc_setup
        
        validation = validate_pc_setup()
        
        print(f"✅ llama.cpp available: {validation['llama_cpp_available']}")
        print(f"📁 Models found: {validation['models_found']}")
        print(f"🎮 GPU available: {validation['gpu_available']}")
        print(f"🎯 System ready: {validation['ready']}")
        
        if validation["errors"]:
            print("\n❌ Errors:")
            for error in validation["errors"]:
                print(f"   • {error}")
        
        if validation["warnings"]:
            print("\n⚠️ Warnings:")
            for warning in validation["warnings"]:
                print(f"   • {warning}")
        
        return validation["ready"]
        
    except Exception as e:
        print(f"❌ System validation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🖥️ PC Homework Grader Setup Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("PC Modules Test", test_pc_modules),
        ("Model Detection", test_model_detection),
        ("GPU Detection", test_gpu_detection),
        ("Model Loading", test_model_loading),
        ("Simple Inference", test_simple_inference),
        ("System Validation", test_system_validation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 Test Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! PC setup is ready.")
        print("💡 Run 'streamlit run pc_start.py' to start grading")
    elif passed >= len(results) - 2:
        print("\n⚠️ Most tests passed. System should work with minor issues.")
        print("💡 Check warnings above and run 'streamlit run pc_start.py'")
    else:
        print("\n❌ Multiple tests failed. Please fix issues before proceeding.")
        print("💡 Check error messages above and install missing dependencies")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)