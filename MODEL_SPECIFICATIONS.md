# Large Language Model Specifications

## System Overview

This document details the exact models, sizes, and configurations used in our automated homework grading system.

---

## Model 1: Qwen 3.0 Coder (Technical Analysis)

### Basic Information
- **Model Name**: Qwen 3.0 Coder 30B Instruct
- **Developer**: Alibaba Cloud (Qwen Team)
- **Model ID**: `hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest`
- **Base Architecture**: Transformer decoder
- **Training Focus**: Code understanding and generation

### Model Size
- **Parameters**: 30 billion (30B)
- **Quantization**: 8-bit (Q8_0)
- **Model File Size**: ~32GB (quantized)
- **Original Size**: ~60GB (FP16)
- **Context Window**: 32,768 tokens
- **Vocabulary Size**: 151,936 tokens

### Hardware Requirements
- **Minimum RAM**: 32GB
- **Recommended RAM**: 64GB
- **GPU VRAM** (optional): 24GB+
- **Storage**: 35GB free space

### Performance Characteristics
- **Load Time**: 45-60 seconds (first request)
- **Inference Speed**: 40-60 tokens/second
- **Latency**: 15-25 seconds per request
- **Memory Usage**: ~30GB during inference

### Configuration
```python
{
    "temperature": 0.3,        # Low for consistency
    "max_tokens": 2000,        # Technical analysis
    "top_p": 0.9,             # Nucleus sampling
    "top_k": 40,              # Top-k sampling
    "repeat_penalty": 1.1,    # Reduce repetition
    "num_ctx": 8192,          # Context window used
    "num_predict": 2000       # Max output tokens
}
```

### Specialization
- **Trained on**: GitHub code, Stack Overflow, technical documentation
- **Languages**: Python, R, JavaScript, Java, C++, SQL, and 80+ more
- **Strengths**:
  - Code structure analysis
  - Bug detection
  - Best practices identification
  - Algorithm evaluation
  - Technical documentation understanding

### Use in Our System
- **Role**: Technical code analysis (Layer 3)
- **Input**: Student code + template + solution + validation results
- **Output**: Code strengths, suggestions, technical observations
- **Prompt Length**: ~3,000-5,000 tokens
- **Response Length**: ~1,000-1,500 tokens

---

## Model 2: Gemma 3.0 (Feedback Generation)

### Basic Information
- **Model Name**: Google Gemma 3.0 27B Instruct
- **Developer**: Google DeepMind
- **Model ID**: `gemma3:27b-it-q8_0`
- **Base Architecture**: Transformer decoder
- **Training Focus**: Instruction following and natural language generation

### Model Size
- **Parameters**: 27 billion (27B)
- **Quantization**: 8-bit (Q8_0)
- **Model File Size**: ~28GB (quantized)
- **Original Size**: ~54GB (FP16)
- **Context Window**: 8,192 tokens
- **Vocabulary Size**: 256,000 tokens

### Hardware Requirements
- **Minimum RAM**: 32GB
- **Recommended RAM**: 64GB
- **GPU VRAM** (optional): 24GB+
- **Storage**: 30GB free space

### Performance Characteristics
- **Load Time**: 40-55 seconds (first request)
- **Inference Speed**: 35-50 tokens/second
- **Latency**: 20-30 seconds per request
- **Memory Usage**: ~28GB during inference

### Configuration
```python
{
    "temperature": 0.3,        # Low for consistency
    "max_tokens": 3000,        # Verbose feedback
    "top_p": 0.9,             # Nucleus sampling
    "top_k": 40,              # Top-k sampling
    "repeat_penalty": 1.1,    # Reduce repetition
    "num_ctx": 8192,          # Context window used
    "num_predict": 3000       # Max output tokens
}
```

### Specialization
- **Trained on**: Web text, books, academic papers, instruction datasets
- **Strengths**:
  - Natural language generation
  - Instruction following
  - Pedagogical feedback
  - Comprehensive explanations
  - Structured output generation

### Use in Our System
- **Role**: Comprehensive feedback generation (Layer 4)
- **Input**: Student markdown + code summary + rubric + validation results
- **Output**: Instructor comments, detailed feedback sections
- **Prompt Length**: ~2,000-4,000 tokens
- **Response Length**: ~1,500-2,500 tokens

---

## Alternative Model: GPT-OSS 120B

### Basic Information
- **Model Name**: GPT-OSS 120B
- **Developer**: Open-source community
- **Model ID**: `gpt-oss:120b`
- **Parameters**: 120 billion (120B)
- **Quantization**: 4-bit or 8-bit

### When to Use
- **Scenario**: Maximum reasoning capability needed
- **Trade-offs**: 
  - ✅ More powerful reasoning
  - ✅ Better at complex analysis
  - ❌ Slower inference (40-60s)
  - ❌ Higher memory usage (70GB+)
  - ❌ May include internal reasoning text

### Performance
- **Load Time**: 90-120 seconds
- **Inference Speed**: 20-30 tokens/second
- **Latency**: 40-60 seconds per request
- **Memory Usage**: ~70GB

---

## Deployment Backends

### Option 1: Ollama (Default)
- **Platform**: Cross-platform (macOS, Linux, Windows)
- **Installation**: `brew install ollama` or download from ollama.ai
- **Model Management**: `ollama pull <model>`
- **API**: REST API on localhost:11434
- **Advantages**: Easy setup, good compatibility
- **Disadvantages**: Slower than MLX on Apple Silicon

### Option 2: MLX (Apple Silicon)
- **Platform**: macOS with M1/M2/M3 chips
- **Installation**: `pip install mlx-lm`
- **Model Management**: `mlx_lm.download --model <model>`
- **API**: Python library
- **Advantages**: 1.5-2x faster on Apple hardware
- **Disadvantages**: Apple Silicon only

### Option 3: Distributed MLX
- **Platform**: Multiple networked Mac Studios
- **Setup**: Custom distributed client
- **Advantages**: True parallel processing, highest throughput
- **Disadvantages**: Complex setup, requires multiple machines

---

## Parallel Processing Performance

### Sequential Execution
```
Qwen Analysis:  20-30 seconds
    ↓
Gemma Feedback: 25-35 seconds
    ↓
Total:          45-65 seconds
```

### Parallel Execution
```
Qwen Analysis:  20-30 seconds  ┐
                                ├→ max(20-30, 25-35) = 25-35 seconds
Gemma Feedback: 25-35 seconds  ┘
```

### Speedup Metrics
- **Theoretical Maximum**: 2.0x
- **Actual Achieved**: 1.8-2.0x
- **Overhead**: <10%
- **Throughput Increase**: 2x more submissions per hour

---

## Cost Analysis

### Hardware Costs (One-time)
- **Mac Studio M2 Ultra**: $4,000-$6,000
- **High-end PC with RTX 4090**: $3,000-$5,000
- **Server with A100 GPU**: $10,000-$15,000

### Operating Costs (Ongoing)
- **Electricity**: ~$0.50-$1.00 per day
- **Maintenance**: Minimal
- **Per-submission cost**: <$0.01 (amortized)

### Time Savings
- **Manual grading**: 15-20 minutes per submission
- **Automated grading**: 30-45 seconds per submission
- **Time saved**: ~95% reduction
- **ROI**: System pays for itself after ~300 submissions

---

## Model Selection Rationale

### Why Qwen 3.0 Coder?
1. **Specialized for code**: Better than general models at code analysis
2. **Right size**: 30B is sweet spot (fast + capable)
3. **Multi-language**: Supports R, Python, SQL, etc.
4. **Open-source**: No API costs, runs locally

### Why Gemma 3.0?
1. **Instruction following**: Excellent at following complex prompts
2. **Clean output**: Less likely to include internal reasoning
3. **Verbose**: Generates detailed, comprehensive feedback
4. **Efficient**: Good performance at 27B size

### Why Not One Large Model?
- **Single 120B model**: Slower (60-90s), less specialized
- **Dual specialized**: Faster (30-45s), better at specific tasks
- **Empirical testing**: Dual approach provides best quality/speed balance

---

## Future Model Considerations

### Potential Upgrades
1. **Qwen 3.5 Coder**: When released, may offer better code understanding
2. **Gemma 4.0**: Future versions with improved instruction following
3. **Fine-tuned models**: Custom models trained on grading data
4. **Mixture of Experts**: Dynamic model selection based on task

### Research Directions
1. **Model distillation**: Smaller, faster models with similar quality
2. **Quantization optimization**: Better 4-bit quantization
3. **Prompt optimization**: Automated prompt engineering
4. **Multi-modal**: Support for images, diagrams in notebooks

