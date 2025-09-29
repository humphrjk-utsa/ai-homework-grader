#!/usr/bin/env python3
"""
PC Configuration for llama.cpp-based homework grader
Optimized for Windows/Linux systems
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional

# PC-specific configuration
PC_CONFIG = {
    # Model preferences (in order of preference) - FLOATING POINT VERSIONS ONLY
    "preferred_code_models": [
        "qwen2.5-coder-32b-instruct-fp16",
        "qwen2.5-coder-32b-instruct-bf16", 
        "qwen2.5-coder-14b-instruct-fp16",
        "qwen2.5-coder-14b-instruct-bf16",
        "qwen2.5-coder-7b-instruct-fp16",
        "qwen2.5-coder-7b-instruct-bf16",
        "codellama-34b-instruct-fp16",
        "codellama-13b-instruct-fp16",
        "codellama-7b-instruct-fp16"
    ],
    
    "preferred_feedback_models": [
        "llama-3.1-70b-instruct-fp16",
        "llama-3.1-70b-instruct-bf16",
        "llama-3.1-8b-instruct-fp16", 
        "llama-3.1-8b-instruct-bf16",
        "llama-3-70b-instruct-fp16",
        "llama-3-8b-instruct-fp16",
        "mistral-7b-instruct-fp16",
        "phi-3-medium-fp16",
        "phi-3-mini-fp16"
    ],
    
    # Quantization preferences (avoid these, prefer FP16/BF16)
    "avoid_quantized_patterns": [
        "q4_k_m", "q4_k_s", "q5_k_m", "q5_k_s", 
        "q8_0", "q6_k", "q4_0", "q5_0",
        "int4", "int8", "4bit", "8bit"
    ],
    
    # Performance settings
    "performance": {
        "enable_gpu_acceleration": True,
        "max_context_length": 4096,
        "default_max_tokens": 2000,
        "batch_size": 512,
        "thread_count": "auto",  # Will be determined automatically
        "memory_mapping": True,
        "use_half_precision": True
    },
    
    # Model directories to search
    "model_directories": [
        "~/.cache/lm-studio/models",
        "~/AppData/Roaming/LMStudio/models",  # Windows
        "~/.local/share/LMStudio/models",     # Linux
        "~/.ollama/models",
        "~/AppData/Local/Ollama/models",      # Windows
        "~/.cache/huggingface/hub",
        "./models",
        "../models",
        "~/models",
        "~/Documents/models"
    ],
    
    # Features
    "features": {
        "enable_parallel_processing": False,  # Not supported yet for PC
        "enable_batch_optimization": True,
        "enable_model_caching": True,
        "enable_progress_indicators": True,
        "auto_model_selection": True
    },
    
    # Grading weights
    "grading_weights": {
        "technical_analysis": 0.6,
        "comprehensive_feedback": 0.4,
        "code_correctness": 0.3,
        "methodology": 0.25,
        "communication": 0.25,
        "best_practices": 0.2
    }
}

def get_pc_config() -> Dict[str, Any]:
    """Get PC configuration"""
    return PC_CONFIG.copy()

def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    return PC_CONFIG.get("features", {}).get(feature_name, False)

def get_model_directories() -> List[str]:
    """Get expanded model directories"""
    directories = []
    
    for dir_path in PC_CONFIG["model_directories"]:
        expanded_path = Path(dir_path).expanduser()
        if expanded_path.exists() and expanded_path.is_dir():
            directories.append(str(expanded_path))
    
    return directories

def get_performance_settings() -> Dict[str, Any]:
    """Get performance settings"""
    settings = PC_CONFIG["performance"].copy()
    
    # Auto-determine thread count if needed
    if settings["thread_count"] == "auto":
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        settings["thread_count"] = max(4, int(cpu_count * 0.75))
    
    return settings

def detect_gpu_capabilities() -> Dict[str, Any]:
    """Detect GPU capabilities for optimization"""
    gpu_info = {
        "nvidia_available": False,
        "amd_available": False,
        "gpu_memory_gb": 0,
        "recommended_layers": 0
    }
    
    try:
        # Check for NVIDIA GPU
        import subprocess
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            gpu_info["nvidia_available"] = True
            memory_mb = int(result.stdout.strip().split('\n')[0])
            gpu_info["gpu_memory_gb"] = memory_mb / 1024
            
            # Recommend GPU layers based on memory
            if gpu_info["gpu_memory_gb"] >= 24:
                gpu_info["recommended_layers"] = -1  # Use all layers
            elif gpu_info["gpu_memory_gb"] >= 12:
                gpu_info["recommended_layers"] = 40
            elif gpu_info["gpu_memory_gb"] >= 8:
                gpu_info["recommended_layers"] = 25
            elif gpu_info["gpu_memory_gb"] >= 6:
                gpu_info["recommended_layers"] = 15
            else:
                gpu_info["recommended_layers"] = 0  # CPU only
                
    except Exception:
        pass
    
    try:
        # Check for AMD GPU (ROCm)
        result = subprocess.run(['rocm-smi'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            gpu_info["amd_available"] = True
            gpu_info["recommended_layers"] = 20  # Conservative for AMD
    except Exception:
        pass
    
    return gpu_info

def get_optimal_model_settings(model_size_gb: float) -> Dict[str, Any]:
    """Get optimal settings based on model size"""
    gpu_info = detect_gpu_capabilities()
    
    settings = {
        "n_gpu_layers": 0,
        "n_threads": get_performance_settings()["thread_count"],
        "n_ctx": 4096,
        "n_batch": 512,
        "use_mmap": True,
        "use_mlock": False
    }
    
    # Adjust based on GPU availability and model size
    if gpu_info["nvidia_available"] or gpu_info["amd_available"]:
        if model_size_gb <= gpu_info.get("gpu_memory_gb", 0) * 0.8:  # 80% of GPU memory
            settings["n_gpu_layers"] = gpu_info["recommended_layers"]
        else:
            # Partial GPU offloading
            settings["n_gpu_layers"] = max(0, gpu_info["recommended_layers"] // 2)
    
    # Adjust context and batch size for larger models
    if model_size_gb > 30:
        settings["n_ctx"] = 2048  # Reduce context for very large models
        settings["n_batch"] = 256
    elif model_size_gb > 15:
        settings["n_ctx"] = 3072
        settings["n_batch"] = 384
    
    return settings

def validate_pc_setup() -> Dict[str, Any]:
    """Validate PC setup for homework grading"""
    validation = {
        "llama_cpp_available": False,
        "models_found": 0,
        "gpu_available": False,
        "recommended_setup": [],
        "warnings": [],
        "errors": []
    }
    
    # Check llama-cpp-python
    try:
        import llama_cpp
        validation["llama_cpp_available"] = True
    except ImportError:
        validation["errors"].append("llama-cpp-python not installed. Run: pip install llama-cpp-python")
    
    # Check for models
    from pc_llamacpp_client import PCLlamaCppClient
    client = PCLlamaCppClient()
    models = client.list_available_models()
    validation["models_found"] = len(models)
    
    if validation["models_found"] == 0:
        validation["warnings"].append("No GGUF models found. Download models to continue.")
        validation["recommended_setup"].append("Download GGUF models from HuggingFace or use LM Studio")
    
    # Check GPU
    gpu_info = detect_gpu_capabilities()
    validation["gpu_available"] = gpu_info["nvidia_available"] or gpu_info["amd_available"]
    
    if not validation["gpu_available"]:
        validation["warnings"].append("No GPU detected. CPU inference will be slower.")
        validation["recommended_setup"].append("Consider using a GPU for faster inference")
    
    # Overall status
    validation["ready"] = (validation["llama_cpp_available"] and 
                          validation["models_found"] > 0)
    
    return validation

def print_pc_setup_info():
    """Print PC setup information"""
    print("🖥️ PC Homework Grader Setup Information")
    print("=" * 50)
    
    validation = validate_pc_setup()
    
    print(f"✅ llama.cpp available: {validation['llama_cpp_available']}")
    print(f"📁 GGUF models found: {validation['models_found']}")
    print(f"🎮 GPU available: {validation['gpu_available']}")
    
    if validation["ready"]:
        print("\n🎉 System ready for PC-based grading!")
    else:
        print("\n⚠️ Setup incomplete. Please address the following:")
        
        for error in validation["errors"]:
            print(f"❌ {error}")
        
        for warning in validation["warnings"]:
            print(f"⚠️ {warning}")
        
        if validation["recommended_setup"]:
            print("\n💡 Recommended setup steps:")
            for step in validation["recommended_setup"]:
                print(f"   • {step}")
    
    # Show GPU info if available
    gpu_info = detect_gpu_capabilities()
    if gpu_info["nvidia_available"]:
        print(f"\n🎮 NVIDIA GPU detected: {gpu_info['gpu_memory_gb']:.1f}GB VRAM")
        print(f"   Recommended GPU layers: {gpu_info['recommended_layers']}")
    elif gpu_info["amd_available"]:
        print(f"\n🎮 AMD GPU detected (ROCm)")
        print(f"   Recommended GPU layers: {gpu_info['recommended_layers']}")

if __name__ == "__main__":
    print_pc_setup_info()