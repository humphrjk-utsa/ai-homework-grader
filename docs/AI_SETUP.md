# Local AI Model Setup Guide

This guide will help you set up a local AI model (OS120) for enhanced homework grading.

## 🤖 Why Use Local AI?

- **Privacy**: Student data stays on your machine
- **Customization**: Train the model on your specific grading style
- **Detailed Feedback**: Rich, contextual feedback for students
- **Cost Effective**: No API fees for large batches of grading
- **Offline Capability**: Grade assignments without internet

## 📋 Prerequisites

- **System Requirements**: 
  - 8GB+ RAM (16GB recommended)
  - 10GB+ free disk space
  - macOS, Linux, or Windows
- **Python 3.8+** (already installed for this project)

## 🛠 Installation Steps

### Step 1: Install Ollama

Ollama is a tool for running large language models locally.

**macOS:**
```bash
# Download and install from website
curl -fsSL https://ollama.ai/install.sh | sh

# Or using Homebrew
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download the installer from [ollama.ai](https://ollama.ai/download)

### Step 2: Start Ollama Service

```bash
# Start the Ollama service
ollama serve
```

This will start the Ollama API server on `http://localhost:11434`

### Step 3: Install the OS120 Model

In a new terminal window:

```bash
# Pull the OS120 model (this may take 10-30 minutes depending on your internet)
ollama pull OS120

# Alternative models you can try:
# ollama pull llama2:7b        # Smaller, faster
# ollama pull codellama:7b     # Specialized for code
# ollama pull mistral:7b       # Good balance of speed and quality
```

### Step 4: Test the Installation

```bash
# Test that the model works
ollama run OS120 "Hello, can you help me grade programming assignments?"
```

You should see a response from the AI model.

### Step 5: Verify in Homework Grader

1. Start your homework grader application:
   ```bash
   cd homework_grader
   python run_grader.py
   ```

2. Go to "Grade Submissions" page
3. You should see "🟢 Local AI Model (OS120) Connected"

## 🔧 Configuration Options

### Model Selection

You can change the model by editing `ai_grader.py`:

```python
# In the LocalAIClient class
def __init__(self, model_name="OS120", base_url="http://localhost:11434"):
    # Change model_name to any installed model:
    # "llama2:7b", "codellama:7b", "mistral:7b", etc.
```

### Performance Tuning

Edit the generation parameters in `ai_grader.py`:

```python
payload = {
    "model": self.model_name,
    "prompt": prompt,
    "stream": False,
    "options": {
        "temperature": 0.3,      # Lower = more consistent, Higher = more creative
        "max_tokens": 2000,      # Maximum response length
        "top_p": 0.9,           # Nucleus sampling
        "repeat_penalty": 1.1    # Avoid repetition
    }
}
```

## 🚀 Advanced Setup

### Multiple Models for Different Tasks

You can set up different models for different types of assignments:

```python
# In ai_grader.py, modify the LocalAIClient initialization
class AIGrader:
    def __init__(self, grader):
        # ... existing code ...
        
        # Use different models based on assignment type
        self.models = {
            "python": LocalAIClient("codellama:7b"),
            "r_stats": LocalAIClient("OS120"),
            "general": LocalAIClient("mistral:7b")
        }
```

### GPU Acceleration (Optional)

If you have an NVIDIA GPU, you can enable GPU acceleration:

```bash
# Install CUDA support for Ollama (Linux/Windows)
# This is automatically detected on macOS with Apple Silicon

# Check if GPU is being used
ollama ps
```

### Custom Model Fine-tuning

For advanced users, you can fine-tune models on your specific grading data:

1. Export your grading history
2. Create a training dataset
3. Use Ollama's fine-tuning capabilities
4. Deploy your custom model

## 🔍 Troubleshooting

### Common Issues

**"Local AI Model Not Available"**
- Check if Ollama is running: `ollama ps`
- Restart Ollama: `ollama serve`
- Verify model is installed: `ollama list`

**Slow Response Times**
- Try a smaller model: `ollama pull llama2:7b`
- Reduce max_tokens in configuration
- Close other applications to free up RAM

**Out of Memory Errors**
- Use a smaller model (7B instead of 13B parameters)
- Reduce context length
- Add more RAM to your system

**Connection Refused**
- Check if Ollama is running on port 11434
- Try restarting Ollama service
- Check firewall settings

### Performance Optimization

**For Faster Grading:**
- Use smaller models (7B parameters)
- Reduce temperature to 0.1 for more consistent responses
- Batch process submissions during off-hours

**For Better Quality:**
- Use larger models (13B+ parameters)
- Increase temperature to 0.5 for more nuanced feedback
- Provide more detailed rubrics and examples

## 📊 Model Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| llama2:7b | 3.8GB | Fast | Good | Quick grading, large batches |
| codellama:7b | 3.8GB | Fast | Excellent | Programming assignments |
| mistral:7b | 4.1GB | Medium | Very Good | General assignments |
| OS120 | Varies | Medium | Excellent | Detailed analysis |
| llama2:13b | 7.3GB | Slow | Excellent | High-quality feedback |

## 🔐 Privacy and Security

- **Data Privacy**: All processing happens locally
- **No Internet Required**: Once models are downloaded
- **Student Privacy**: No data sent to external services
- **Compliance**: Meets most institutional privacy requirements

## 💡 Tips for Best Results

1. **Clear Rubrics**: Provide detailed, specific grading criteria
2. **Example Solutions**: Include reference solutions for comparison
3. **Consistent Prompts**: Use standardized prompting for fairness
4. **Human Review**: Always review AI grades before finalizing
5. **Iterative Improvement**: Refine prompts based on results

## 🆘 Getting Help

- **Ollama Documentation**: [ollama.ai/docs](https://ollama.ai/docs)
- **Model Hub**: [ollama.ai/library](https://ollama.ai/library)
- **Community**: [GitHub Issues](https://github.com/jmorganca/ollama/issues)

## 🔄 Updating

Keep your models updated for best performance:

```bash
# Update Ollama
ollama update

# Update specific model
ollama pull OS120

# List installed models
ollama list
```

---

Once you have this set up, your homework grader will provide much more detailed, contextual feedback to students while maintaining complete privacy and control over the grading process!