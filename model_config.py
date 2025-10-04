"""
Model Configuration for AI Homework Grader

This file controls which AI model is used for grading.
Different models have different strengths:

MLX MODELS (Apple Silicon - Recommended):
- mlx-community/gemma-3-27b-it-bf16: Best for clean, verbose feedback (RECOMMENDED)
- lmstudio-community/gpt-oss-120b-MLX-8bit: Very powerful but may include thinking text

OLLAMA MODELS (Cross-platform):
- gemma3:27b: Better at following instructions, cleaner output
- gpt-oss:120b: Very powerful, but may include internal thinking/reasoning
- deepseek-r1:70b: Excellent reasoning, but verbose with thinking process
- qwen3-coder:30b: Great for code analysis

RECOMMENDATION: Use MLX Gemma for cleaner, more verbose, personalized feedback
"""

# Primary model for grading (change this to switch models)
# MLX Gemma (if you have it) - BEST OPTION
PRIMARY_GRADING_MODEL = "mlx-community/gemma-3-27b-it-bf16"  # Your MLX Gemma model

# Alternative models (uncomment to use)
# PRIMARY_GRADING_MODEL = "gemma3:27b"  # Ollama Gemma
# PRIMARY_GRADING_MODEL = "gpt-oss:120b"  # Very powerful but may include thinking text
# PRIMARY_GRADING_MODEL = "deepseek-r1:70b"  # Excellent reasoning
# PRIMARY_GRADING_MODEL = "qwen3-coder:30b"  # Best for code analysis

# Fallback models if primary is not available
FALLBACK_MODELS = [
    "mlx-community/gemma-3-27b-it-bf16",  # MLX Gemma (best)
    "lmstudio-community/gpt-oss-120b-MLX-8bit",  # MLX GPT-OSS
    "gemma3:27b",  # Ollama Gemma
    "gpt-oss:120b",  # Ollama GPT-OSS
    "deepseek-r1:70b",
    "qwen3-coder:30b",
    "llama4:latest"
]

# Model-specific settings
MODEL_SETTINGS = {
    # MLX Models (Apple Silicon optimized)
    "mlx-community/gemma-3-27b-it-bf16": {
        "temperature": 0.3,
        "max_tokens": 3000,  # More tokens for verbose feedback
        "description": "MLX Gemma - Clean, verbose, personalized feedback (BEST)"
    },
    "lmstudio-community/gpt-oss-120b-MLX-8bit": {
        "temperature": 0.3,
        "max_tokens": 2500,
        "description": "MLX GPT-OSS - Very powerful, may include thinking text"
    },
    # Ollama Models
    "gemma3:27b": {
        "temperature": 0.3,
        "max_tokens": 3000,
        "description": "Ollama Gemma - Clean, verbose, personalized feedback"
    },
    "gpt-oss:120b": {
        "temperature": 0.3,
        "max_tokens": 2500,
        "description": "Ollama GPT-OSS - Very powerful, may include thinking text"
    },
    "deepseek-r1:70b": {
        "temperature": 0.3,
        "max_tokens": 2500,
        "description": "Excellent reasoning, verbose"
    },
    "qwen3-coder:30b": {
        "temperature": 0.3,
        "max_tokens": 2000,
        "description": "Best for code analysis"
    }
}

def get_model_config(model_name=None):
    """Get configuration for specified model or primary model"""
    if model_name is None:
        model_name = PRIMARY_GRADING_MODEL
    
    return MODEL_SETTINGS.get(model_name, {
        "temperature": 0.3,
        "max_tokens": 2000,
        "description": "Default settings"
    })
