## 3. Large Language Models

### 3.1 Model Selection

We employ two specialized LLMs in parallel:

#### Model 1: Qwen 3.0 Coder (Technical Analysis)
- **Full Name**: Qwen 3.0 Coder 30B Instruct
- **Parameters**: 30 billion
- **Quantization**: 8-bit (Q8_0)
- **Model ID**: `hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest`
- **Purpose**: Code analysis and technical evaluation
- **Specialization**: Trained specifically for code understanding
- **Context Window**: 32,768 tokens
- **Temperature**: 0.3 (deterministic)
- **Max Tokens**: 2,000

**Rationale**: Qwen 3.0 Coder is specifically fine-tuned for code analysis tasks, making it ideal for evaluating:
- Code structure and organization
- Algorithm correctness
- Best practices adherence
- Technical implementation quality

#### Model 2: Gemma 3.0 (Feedback Generation)
- **Full Name**: Google Gemma 3.0 27B Instruct
- **Parameters**: 27 billion
- **Quantization**: 8-bit (Q8_0)
- **Model ID**: `gemma3:27b-it-q8_0`
- **Purpose**: Comprehensive feedback and pedagogical assessment
- **Specialization**: Instruction-following and natural language generation
- **Context Window**: 8,192 tokens
- **Temperature**: 0.3 (deterministic)
- **Max Tokens**: 3,000

**Alternative**: GPT-OSS 120B
- **Parameters**: 120 billion
- **Model ID**: `gpt-oss:120b`
- **Use Case**: When maximum reasoning capability is needed
- **Trade-off**: Slower inference, may include internal reasoning text



### 3.2 Model Deployment Options

#### Option A: Ollama (Cross-platform)
- **Backend**: Ollama API server
- **Deployment**: Local or networked
- **Hardware**: CPU or GPU
- **Memory**: ~70GB for 120B models, ~30GB for 30B models
- **Load Time**: 45-60 seconds (first request)
- **Inference Time**: 15-30 seconds per request

#### Option B: MLX (Apple Silicon Optimized)
- **Backend**: Apple MLX framework
- **Deployment**: Local on M1/M2/M3 Macs
- **Hardware**: Apple Silicon GPU
- **Memory**: Optimized unified memory usage
- **Load Time**: 30-45 seconds (first request)
- **Inference Time**: 10-20 seconds per request
- **Advantage**: 1.5-2x faster than Ollama on Apple hardware

#### Option C: Distributed MLX (Multi-Machine)
- **Backend**: Custom distributed system
- **Deployment**: Multiple Mac Studios networked
- **Hardware**: Dedicated machine per model
- **Memory**: Distributed across machines
- **Load Time**: Models pre-loaded
- **Inference Time**: 8-15 seconds per request
- **Advantage**: True parallel processing, highest throughput

### 3.3 Model Configuration

```python
MODEL_SETTINGS = {
    "qwen3-coder:30b": {
        "temperature": 0.3,      # Low for consistency
        "max_tokens": 2000,      # Technical analysis
        "top_p": 0.9,
        "repeat_penalty": 1.1
    },
    "gemma3:27b": {
        "temperature": 0.3,      # Low for consistency
        "max_tokens": 3000,      # Verbose feedback
        "top_p": 0.9,
        "repeat_penalty": 1.1
    }
}
```

