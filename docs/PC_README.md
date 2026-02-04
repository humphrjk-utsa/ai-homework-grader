# PC Homework Grader - llama.cpp Branch

This branch provides a PC-optimized version of the homework grader using llama.cpp for cross-platform compatibility on Windows and Linux systems.

## 🖥️ PC-Specific Features

- **llama.cpp Integration**: Uses GGUF models for efficient inference
- **GPU Acceleration**: Supports NVIDIA CUDA and AMD ROCm
- **Automatic Model Detection**: Scans common model directories
- **Memory Optimization**: Efficient memory usage for large models
- **Cross-Platform**: Works on Windows, Linux, and macOS

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Basic installation
pip install llama-cpp-python streamlit pandas numpy scikit-learn

# For NVIDIA GPU support
pip install llama-cpp-python[cuda]

# For AMD GPU support (Linux)
pip install llama-cpp-python[rocm]
```

### 2. Download Models

You need GGUF format models. Recommended sources:

**Option A: LM Studio (Easiest)**
1. Download [LM Studio](https://lmstudio.ai/)
2. Search and download models like:
   - `Qwen2.5-Coder-32B-Instruct-GGUF`
   - `Meta-Llama-3.1-70B-Instruct-GGUF`
   - `Mistral-7B-Instruct-v0.3-GGUF`

**Option B: Direct Download (FLOATING POINT ONLY)**
```bash
# Download FP16 versions for maximum accuracy
huggingface-cli download Qwen/Qwen2.5-Coder-32B-Instruct-GGUF qwen2.5-coder-32b-instruct-fp16.gguf --local-dir ./models
huggingface-cli download meta-llama/Llama-3.1-8B-Instruct-GGUF llama-3.1-8b-instruct-fp16.gguf --local-dir ./models

# Alternative: BF16 versions (also high quality)
huggingface-cli download Qwen/Qwen2.5-Coder-14B-Instruct-GGUF qwen2.5-coder-14b-instruct-bf16.gguf --local-dir ./models
```

⚠️ **AVOID quantized versions** (files with q4, q8, int4, etc. in the name) as they reduce grading accuracy.

### 3. Run the PC Grader

```bash
# Start the PC-optimized grader
streamlit run pc_start.py

# Or check system setup first
python pc_config.py
```

## 📁 File Structure

```
homework_grader/
├── pc_start.py              # Main PC application
├── pc_llamacpp_client.py    # llama.cpp client
├── pc_two_model_grader.py   # Two-model grading system
├── pc_config.py             # PC-specific configuration
├── PC_README.md             # This file
└── models/                  # Place GGUF models here (optional)
```

## 🤖 Model Recommendations

### For Code Analysis (FLOATING POINT VERSIONS ONLY)
- **Qwen2.5-Coder-32B-Instruct-FP16** (Best quality, requires 64GB+ RAM)
- **Qwen2.5-Coder-14B-Instruct-FP16** (Good balance, requires 28GB+ RAM)
- **Qwen2.5-Coder-7B-Instruct-FP16** (Lightweight, requires 14GB+ RAM)
- **CodeLlama-34B-Instruct-FP16** (Alternative, good for code, requires 68GB+ RAM)

### For Feedback Generation (FLOATING POINT VERSIONS ONLY)
- **Llama-3.1-70B-Instruct-FP16** (Best quality, requires 140GB+ RAM)
- **Llama-3.1-8B-Instruct-FP16** (Good balance, requires 16GB+ RAM)
- **Mistral-7B-Instruct-FP16** (Lightweight, requires 14GB+ RAM)
- **Phi-3-Medium-FP16** (Efficient, requires 14GB+ RAM)

⚠️ **IMPORTANT**: This system is configured to use **FLOATING POINT models only** (FP16/BF16) for maximum accuracy. Quantized models (Q4, Q8, etc.) are avoided to ensure the highest quality grading results.

## ⚙️ Configuration

### GPU Settings

The system automatically detects your GPU and optimizes settings:

```python
# Automatic GPU detection
- NVIDIA: Uses CUDA acceleration
- AMD: Uses ROCm acceleration  
- CPU: Falls back to optimized CPU inference
```

### Memory Requirements (FLOATING POINT MODELS)

| Model Size | Precision | RAM Required | GPU VRAM | Performance |
|------------|-----------|--------------|----------|-------------|
| 7B         | FP16      | 14GB        | 14GB     | Good        |
| 8B         | FP16      | 16GB        | 16GB     | Good        |
| 14B        | FP16      | 28GB        | 28GB     | Better      |
| 32B        | FP16      | 64GB        | 64GB     | Best        |
| 70B        | FP16      | 140GB       | 80GB     | Excellent   |

⚠️ **Note**: Floating point models require significantly more memory than quantized versions but provide the highest accuracy for grading tasks.

### Model Directories

The system searches these directories for GGUF models:

- `~/.cache/lm-studio/models` (LM Studio)
- `~/AppData/Roaming/LMStudio/models` (Windows LM Studio)
- `~/.ollama/models` (Ollama)
- `~/.cache/huggingface/hub` (HuggingFace)
- `./models` (Local models folder)

## 🎯 Usage Examples

### Single Submission Grading

```python
from pc_two_model_grader import PCTwoModelGrader

# Initialize grader
grader = PCTwoModelGrader()

# Grade submission
result = grader.grade_submission(
    student_code="library(dplyr)\ndata <- read.csv('file.csv')",
    student_markdown="This analysis explores...",
    solution_code="# Reference solution",
    assignment_info={"title": "Data Cleaning"},
    rubric_elements={"code_correctness": {"weight": 0.4}}
)

print(f"Final Score: {result['final_score']}")
```

### Batch Processing

```python
# Enable batch mode for efficiency
grader.enable_batch_mode()

# Process multiple submissions
results = grader.grade_batch(submissions)
```

### Custom Model Selection

```python
# Use specific models
grader = PCTwoModelGrader(
    code_model_path="./models/qwen2.5-coder-32b.gguf",
    feedback_model_path="./models/llama-3.1-70b.gguf"
)
```

## 🔧 Troubleshooting

### Common Issues

**1. No models found**
```bash
# Check model directories
python -c "from pc_llamacpp_client import PCLlamaCppClient; print(PCLlamaCppClient().list_available_models())"
```

**2. GPU not detected**
```bash
# Check GPU status
nvidia-smi  # For NVIDIA
rocm-smi    # For AMD
```

**3. Out of memory**
- Use smaller models (7B instead of 32B)
- Reduce context length in config
- Enable memory mapping

**4. Slow inference**
- Enable GPU acceleration
- Use quantized models (Q4_K_M)
- Increase thread count

### Performance Optimization

```python
# Optimize for your system
from pc_config import get_optimal_model_settings

settings = get_optimal_model_settings(model_size_gb=20)
print(settings)
```

## 📊 Performance Comparison

| System | Model | Speed | Quality |
|--------|-------|-------|---------|
| RTX 4090 | Qwen2.5-32B | ~30 tok/s | Excellent |
| RTX 3080 | Qwen2.5-14B | ~25 tok/s | Very Good |
| CPU (16 cores) | Qwen2.5-7B | ~8 tok/s | Good |
| M1 Mac | Use MLX branch | ~40 tok/s | Excellent |

## 🆚 Branch Comparison

| Feature | PC Branch (llama.cpp) | MLX Branch (Apple) |
|---------|----------------------|-------------------|
| Platform | Windows/Linux/macOS | macOS only |
| GPU Support | NVIDIA/AMD | Apple Silicon |
| Model Format | GGUF | MLX |
| Memory Usage | Efficient | Very Efficient |
| Setup Complexity | Medium | Easy |

## 🔄 Migration from MLX

If migrating from the MLX branch:

1. **Convert Models**: MLX models need conversion to GGUF
2. **Update Imports**: Change from `mlx_ai_client` to `pc_llamacpp_client`
3. **Adjust Config**: Use `pc_config.py` instead of MLX config
4. **Test Performance**: Benchmark on your hardware

## 🤝 Contributing

To contribute to the PC branch:

1. Test on different hardware configurations
2. Add support for new model formats
3. Optimize performance settings
4. Improve error handling
5. Add more model recommendations

## 📝 License

Same as main project - see LICENSE file.

## 🆘 Support

For PC-specific issues:
- Check GPU drivers are updated
- Verify model file integrity
- Monitor system resources
- Test with smaller models first

For general grading issues, see the main README.md.