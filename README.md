# AI-Powered Homework Grader

🤖 **Comprehensive AI grading system with business analytics focus**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/ai-homework-grader.git
cd ai-homework-grader

# Install dependencies
pip install -r requirements.txt

# Install Ollama (for AI models)
# Windows: Download from https://ollama.ai
# Mac: brew install ollama
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

# Download AI models
ollama pull hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest
ollama pull gemma3:27b-it-q8_0

# Run the application
streamlit run app.py
```

Open your browser to `http://localhost:8501` and start grading! 🎉

## ✨ Features

### 🎓 **Comprehensive AI Grading**
- **Two-Model Architecture**: Qwen 3.0 Coder + Gemma 3.0 for parallel processing
- **Business Analytics Focus**: Tailored feedback for business/analytics courses
- **6 Detailed Feedback Sections**: Reflection, strengths, application, learning, development, recommendations
- **37.5-Point Scale**: Professional academic grading scale
- **Validation System**: Automatic consistency checking and error correction

### 📊 **Professional Reports**
- **PDF Generation**: Comprehensive reports with detailed feedback
- **Code Examples**: Specific R code examples and improvements
- **Professional Formatting**: University-quality academic reports
- **Batch Processing**: Generate reports for entire classes
- **Export Options**: CSV gradebooks and individual PDFs

### 🌐 **Modern Web Interface**
- **Streamlit Application**: Clean, responsive web interface
- **Assignment Management**: Create and configure assignments
- **Batch Upload**: Upload multiple student submissions at once
- **Real-time Grading**: Live progress indicators and status updates
- **Results Dashboard**: Comprehensive viewing and filtering

### 🧠 **AI Training System**
- **Correction Interface**: Review and correct AI assessments
- **Training Data**: Build datasets to improve AI accuracy
- **Performance Analytics**: Track improvement over time
- **Feedback Refinement**: Enhance AI feedback quality

### 🔧 **Cross-Platform Support**
- **Windows & Mac**: Full compatibility
- **Docker Ready**: Containerization support
- **Cloud Deployable**: AWS, GCP, Azure compatible
- **Database Portability**: SQLite for easy deployment

## 📁 Project Structure

```
ai-homework-grader/
├── 📄 app.py                          # Main Streamlit application
├── 🤖 business_analytics_grader.py    # AI grading system
├── 📊 report_generator.py             # PDF report generation
├── 🌐 connect_web_interface.py        # Web grading interface
├── 📋 grading_interface.py            # Results management
├── 🧠 training_interface.py           # AI training system
├── 📝 assignment_manager.py           # Assignment creation
├── ✏️ assignment_editor.py            # Assignment editing
├── 🗄️ grading_database.db            # SQLite database
├── 📚 requirements.txt               # Dependencies
├── 📖 README.md                      # This file
├── 📂 assignments/                   # Assignment templates
├── 📂 submissions/                   # Student work
├── 📂 reports/                       # Generated PDFs
├── 📂 tests/                         # Test suite
├── 📂 docs/                          # Documentation
├── 📂 models/                        # Model interfaces
└── 📂 setup/                         # Installation scripts
```

## 🎯 Use Cases

### 👨‍🏫 **For Educators**
- **Business Analytics Courses**: R programming, data analysis assignments
- **Statistics Classes**: Data exploration and interpretation
- **Research Methods**: Methodology and analysis evaluation
- **Any Programming Course**: Adaptable to different languages

### 🏫 **For Institutions**
- **Scalable Grading**: Handle large class sizes efficiently
- **Consistent Standards**: Uniform grading across sections
- **Quality Assurance**: Detailed feedback for accreditation
- **Time Savings**: Reduce grading time by 80%+

### 👩‍💻 **For Developers**
- **Extensible Architecture**: Easy to add new features
- **Model Flexibility**: Support for different AI models
- **API Integration**: RESTful endpoints for integration
- **Custom Rubrics**: Adaptable to any grading criteria

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- 8GB+ RAM (16GB recommended for large models)
- 10GB+ free disk space
- Internet connection for model downloads

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-homework-grader.git
   cd ai-homework-grader
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Ollama**
   - **Windows**: Download from [ollama.ai](https://ollama.ai)
   - **Mac**: `brew install ollama`
   - **Linux**: `curl -fsSL https://ollama.ai/install.sh | sh`

5. **Download AI models**
   ```bash
   ollama serve  # Start Ollama service
   
   # In another terminal:
   ollama pull hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest
   ollama pull gemma3:27b-it-q8_0
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 📖 Usage Guide

### 1. **Create Assignment**
- Navigate to "Assignment Management"
- Define grading rubric and point values
- Upload template and solution notebooks (optional)

### 2. **Upload Student Work**
- Go to "Upload Submissions"
- Single file upload or batch ZIP upload
- Automatic student name extraction

### 3. **Grade Submissions**
- Select "Grade Submissions"
- Choose individual or batch grading
- AI provides comprehensive feedback automatically

### 4. **Review Results**
- View detailed feedback in "View Results"
- Generate PDF reports with code examples
- Export gradebooks to CSV

### 5. **Train the AI**
- Use "AI Training" to review AI assessments
- Correct scores and feedback as needed
- Improve AI accuracy over time

## 🔧 Configuration

### Model Settings
Edit `business_analytics_grader.py` to customize:
- Model selection and parameters
- Grading rubric weights
- Feedback generation prompts
- Scoring algorithms

### Interface Customization
Modify `app.py` for:
- UI themes and styling
- Page layouts and navigation
- Feature toggles
- Branding and logos

### Database Configuration
SQLite database includes:
- Assignment configurations
- Student information
- Grading history
- Training data

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python tests/test_grading_interface.py
python tests/test_pdf_generation.py
python tests/test_ai_training.py
```

## 📊 Performance

### Benchmarks
- **Grading Speed**: ~60 seconds per submission
- **Parallel Efficiency**: 1.3x speedup with two-model system
- **Memory Usage**: ~4GB RAM for standard models
- **Accuracy**: 90%+ correlation with human graders

### Optimization Tips
- Use quantized models (q8_0) for faster inference
- Enable parallel processing for batch grading
- Allocate sufficient RAM for model loading
- Use SSD storage for better I/O performance

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone and setup development environment
git clone https://github.com/YOUR_USERNAME/ai-homework-grader.git
cd ai-homework-grader
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Run tests
python -m pytest

# Start development server
streamlit run app.py --server.runOnSave true
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama**: For providing the model serving infrastructure
- **Streamlit**: For the excellent web application framework
- **Qwen Team**: For the powerful coding model
- **Google**: For the Gemma language model
- **ReportLab**: For PDF generation capabilities

## 📞 Support

- **Documentation**: Check the `docs/` directory
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join GitHub Discussions for questions
- **Email**: [your-email@domain.com]

## 🗺️ Roadmap

- [ ] Support for additional programming languages
- [ ] Integration with Learning Management Systems (LMS)
- [ ] Advanced analytics and reporting
- [ ] Multi-language interface support
- [ ] Cloud deployment templates
- [ ] Mobile-responsive interface improvements

---

**Made with ❤️ for educators and students worldwide**