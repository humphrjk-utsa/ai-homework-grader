#!/usr/bin/env python3
"""
Configuration for Two-Model Grading System
"""

# Model configurations
MODEL_CONFIG = {
    'code_analyzer': {
        'model_name': 'mlx-community/Qwen3-Coder-30B-A3B-Instruct-bf16',  # Your preferred bf16 model
        'max_tokens': 2400,  # Optimized for speed while maintaining quality
        'temperature': 0.1,  # Low temperature for precise code analysis
        'timeout': 75,  # Optimized timeout
        'fallback_models': [
            'mlx-community/Meta-Llama-3.1-70B-Instruct-4bit',
            'mlx-community/gemma-2-27b-it-4bit'
        ]
    },
    'feedback_generator': {
        'model_name': 'mlx-community/gemma-3-27b-it-bf16',  # Your preferred bf16 model
        'max_tokens': 3800,  # Increased for more verbose, detailed feedback
        'temperature': 0.3,  # Higher temperature for creative feedback
        'timeout': 75,  # Optimized for 27B model
        'fallback_models': [
            'mlx-community/gemma-3-27b-it-8bit',  # Fallback to 8-bit if bf16 fails
            'lmstudio-community/gpt-oss-120b-MLX-8bit',
            'mlx-community/Meta-Llama-3.1-70B-Instruct-4bit'
        ]
    }
}

# Grading weights (adjusted for business analytics students)
GRADING_WEIGHTS = {
    'technical_weight': 0.8,  # 80% technical analysis (reward completion heavily)
    'conceptual_weight': 0.2,  # 20% conceptual understanding (business-focused)
    'completion_bonus': 0.15,  # 15% bonus for completing all requirements
    'business_application_bonus': 0.05,  # 5% bonus for business insights
    'business_student_friendly': True,  # Enable business-student-friendly grading
    'minimum_completion_score': 0.94,  # 94% minimum for students who complete all work
    'target_audience': 'business_analytics'  # Not computer science majors
}

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    'max_code_analysis_time': 180,  # 3 minutes max for code analysis
    'max_feedback_time': 240,  # 4 minutes max for feedback generation
    'max_total_time': 300,  # 5 minutes max total
    'memory_limit_gb': 100  # 100GB memory limit per model
}

# Fallback settings
FALLBACK_CONFIG = {
    'enable_detailed_analyzer_fallback': True,
    'enable_simple_grader_fallback': True,
    'min_score_threshold': 0,  # Minimum score to accept results
    'max_retries': 2
}

# Feature flags
FEATURE_FLAGS = {
    'enable_two_model_system': True,
    'enable_parallel_processing': False,  # Disable for now due to GPU contention
    'enable_caching': True,
    'enable_performance_monitoring': True,
    'debug_mode': False
}

# Assignment-specific configurations
ASSIGNMENT_CONFIGS = {
    'data_cleaning': {
        'focus_areas': ['missing_values', 'outliers', 'data_quality'],
        'required_functions': ['sum(is.na())', 'complete.cases()', 'quantile()', 'IQR()'],
        'bonus_functions': ['ggplot()', 'dplyr', 'tidyr']
    },
    'intro_to_r': {
        'focus_areas': ['data_import', 'basic_operations', 'exploration'],
        'required_functions': ['read_csv()', 'head()', 'str()', 'summary()'],
        'bonus_functions': ['library()', 'getwd()']
    }
}

def get_model_config(model_type: str) -> dict:
    """Get configuration for specific model type"""
    return MODEL_CONFIG.get(model_type, {})

def get_grading_weights() -> dict:
    """Get grading weight configuration"""
    return GRADING_WEIGHTS

def is_feature_enabled(feature: str) -> bool:
    """Check if a feature is enabled"""
    return FEATURE_FLAGS.get(feature, False)

def get_assignment_config(assignment_type: str) -> dict:
    """Get configuration for specific assignment type"""
    return ASSIGNMENT_CONFIGS.get(assignment_type, {})