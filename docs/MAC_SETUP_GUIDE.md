# Homework Grader - Mac Setup Guide

## 🍎 Running on Mac

The homework grader is fully compatible with Mac! Here's how to set it up:

## 📋 Prerequisites

### 1. Python 3.8+
```bash
# Check if Python is installed
python3 --version

# If not installed, install via Homebrew
brew install python3
```

### 2. Ollama (for AI models)
```bash
# Install Ollama on Mac
curl -fsSL https://ollama.ai/install.sh | sh

# Or via Homebrew
brew install ollama
```

## 🚀 Quick Setup

### 1. Copy the homework_grader folder to your Mac
```bash
# If transferring from Windows, you can:
# - Use cloud storage (Google Drive, Dropbox, etc.)
# - Use git to clone/push/pull
# - Use file transfer tools
```

### 2. Install Python dependencies
```bash
cd homework_grader
pip3 install -r requirements.txt
```

### 3. Download AI models
```bash
# Start Ollama service
ollama serve

# In another terminal, download models
ollama pull hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest
ollama pull gemma3:27b-it-q8_0
```

### 4. Run the application
```bash
streamlit run app.py
```

## 🔧 Mac-Specific Considerations

### File Paths
- The app uses relative paths, so it works the same on Mac
- Database and file storage will work identically
- PDF generation works on Mac (reportlab is cross-platform)

### Performance
- **M1/M2 Macs**: Excellent performance with native ARM support
- **Intel Macs**: Good performance, may be slightly slower for AI inference
- **Memory**: 16GB+ RAM recommended for best performance with large models

### Model Options for Mac

#### Option 1: Ollama (Recommended)
```bash
# Standard setup - works on all Macs
ollama pull hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest
ollama pull gemma3:27b-it-q8_0
```

#### Option 2: MLX (M1/M2 Macs only)
```bash
# For Apple Silicon Macs - faster inference
pip install mlx mlx-lm
# The app will automatically detect and use MLX if available
```

## 📁 Directory Structure (Same on Mac)
```
homework_grader/
├── app.py                          # Main application
├── business_analytics_grader.py    # AI grading system
├── *.py                           # Core modules
├── grading_database.db            # SQLite database
├── assignments/                   # Assignment files
├── submissions/                   # Student work
├── reports/                       # Generated PDFs
├── tests/                         # Test files
├── docs/                          # Documentation
├── models/                        # Model interfaces
├── setup/                         # Setup scripts
└── archive/                       # Archived files
```

## 🎯 Mac-Specific Features

### 1. Native Performance
- Uses Mac's native SQLite
- PDF generation optimized for Mac
- File handling uses Mac filesystem

### 2. Integration
- Works with Mac's default PDF viewer
- Integrates with Mac file system
- Can use Mac's notification system

### 3. Development
- Works with Mac development tools
- Compatible with VS Code, PyCharm on Mac
- Git integration works seamlessly

## 🚀 Running the App

### Start the application:
```bash
cd homework_grader
streamlit run app.py
```

### Access the web interface:
- Open browser to: `http://localhost:8501`
- All features work identically to Windows version

## 📊 What Works on Mac

✅ **All Core Features:**
- Assignment creation and management
- Student submission upload (single and batch)
- AI grading with Business Analytics Grader
- Comprehensive feedback generation
- PDF report generation with code examples
- AI training interface
- Results viewing and export

✅ **Cross-Platform Compatibility:**
- Database files transfer between Mac/Windows
- PDF reports open on any system
- Student notebooks work identically
- All file formats supported

✅ **Performance:**
- Two-model AI system (Qwen 3.0 + Gemma 3.0)
- Parallel processing for faster grading
- Efficient memory usage
- Fast PDF generation

## 🔄 Transferring from Windows

### Method 1: Direct Copy
1. Copy entire `homework_grader` folder to Mac
2. Install dependencies: `pip3 install -r requirements.txt`
3. Install Ollama and download models
4. Run: `streamlit run app.py`

### Method 2: Git Repository
```bash
# On Windows (if using git)
git add .
git commit -m "Homework grader setup"
git push

# On Mac
git clone [your-repo]
cd homework_grader
pip3 install -r requirements.txt
# Download models and run
```

### Method 3: Cloud Storage
1. Upload `homework_grader` folder to cloud storage
2. Download on Mac
3. Follow setup steps above

## 🎓 Database Compatibility

The SQLite database is fully compatible between Mac and Windows:
- ✅ All student data transfers
- ✅ Assignment configurations preserved
- ✅ Grading history maintained
- ✅ AI training data intact

## 💡 Mac Tips

### Terminal Commands
```bash
# Check if Ollama is running
ps aux | grep ollama

# Monitor system resources
top -o cpu

# Check available disk space
df -h
```

### Performance Optimization
```bash
# For M1/M2 Macs, ensure you're using ARM Python
python3 -c "import platform; print(platform.machine())"
# Should show 'arm64' for M1/M2

# Install ARM-optimized packages if needed
pip3 install --upgrade --force-reinstall streamlit pandas numpy
```

## 🎉 Ready to Use on Mac!

The homework grader will work identically on Mac with:
- Same user interface
- Same features and functionality  
- Same performance characteristics
- Same file formats and compatibility
- Cross-platform database sharing

Just follow the setup steps above and you'll have a fully functional AI-powered homework grading system on your Mac! 🍎