#!/bin/bash
# Automated Production Setup Script
# Creates clean production version of AI Homework Grader

set -e  # Exit on error

echo "🚀 AI Homework Grader - Production Setup"
echo "=========================================="
echo ""

# Get current directory (old project)
OLD_DIR="$(pwd)"
echo "📂 Current project: $OLD_DIR"

# Set new directory
NEW_DIR="$HOME/GitHub/ai-homework-grader-production"
echo "📂 New project: $NEW_DIR"
echo ""

# Confirm
read -p "Create production version at $NEW_DIR? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 1
fi

# Create new directory
echo "📁 Creating directory structure..."
mkdir -p "$NEW_DIR"
cd "$NEW_DIR"

# Create subdirectories
mkdir -p app
mkdir -p validators
mkdir -p disaggregated_inference
mkdir -p prompt_templates/ollama
mkdir -p rubrics
mkdir -p data/raw
mkdir -p data/processed
mkdir -p reports
mkdir -p submissions
mkdir -p docs
mkdir -p scripts
mkdir -p tests
mkdir -p logs

echo "✅ Directory structure created"

# Create .gitignore
echo "📝 Creating .gitignore..."
cat > .gitignore << 'GITIGNORE_EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
env/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Databases
*.db
*.sqlite
*.sqlite3

# Logs
logs/*.log
*.log

# Reports
reports/**/*.pdf

# Submissions  
submissions/**/*.ipynb
submissions/**/*.py

# Environment
.env
.env.local

# Kiro
.kiro/

# macOS
.DS_Store
.AppleDouble
.LSOverride

# Temporary
*.tmp
*.temp
.mypy_cache/
GITIGNORE_EOF

echo "✅ .gitignore created"

# Copy production files
echo ""
echo "📋 Copying production files..."

# Core application files
echo "  → Core application files..."
cp "$OLD_DIR/connect_web_interface.py" app/ 2>/dev/null || echo "    ⚠️  connect_web_interface.py not found"
cp "$OLD_DIR/business_analytics_grader_v2.py" app/ 2>/dev/null || echo "    ⚠️  business_analytics_grader_v2.py not found"
cp "$OLD_DIR/disaggregated_client.py" app/ 2>/dev/null || echo "    ⚠️  disaggregated_client.py not found"
cp "$OLD_DIR/prompt_manager.py" app/ 2>/dev/null || echo "    ⚠️  prompt_manager.py not found"
cp "$OLD_DIR/grading_validator.py" app/ 2>/dev/null || echo "    ⚠️  grading_validator.py not found"
cp "$OLD_DIR/report_generator.py" app/ 2>/dev/null || echo "    ⚠️  report_generator.py not found"
cp "$OLD_DIR/score_validator.py" app/ 2>/dev/null || echo "    ⚠️  score_validator.py not found"
cp "$OLD_DIR/notebook_executor.py" app/ 2>/dev/null || echo "    ⚠️  notebook_executor.py not found"
cp "$OLD_DIR/submission_preprocessor.py" app/ 2>/dev/null || echo "    ⚠️  submission_preprocessor.py not found"
cp "$OLD_DIR/anonymization_utils.py" app/ 2>/dev/null || echo "    ⚠️  anonymization_utils.py not found"
cp "$OLD_DIR/model_status_display.py" app/ 2>/dev/null || echo "    ⚠️  model_status_display.py not found"
cp "$OLD_DIR/notebook_validation.py" app/ 2>/dev/null || echo "    ⚠️  notebook_validation.py not found"
cp "$OLD_DIR/output_comparator.py" app/ 2>/dev/null || echo "    ⚠️  output_comparator.py not found"
cp "$OLD_DIR/ai_grader.py" app/ 2>/dev/null || echo "    ⚠️  ai_grader.py not found"

# Validators
echo "  → Validators..."
if [ -d "$OLD_DIR/validators" ]; then
    cp -r "$OLD_DIR/validators/"* validators/ 2>/dev/null || true
fi

# Disaggregated inference
echo "  → Disaggregated inference..."
cp "$OLD_DIR/disaggregated_inference/config_current.json" disaggregated_inference/ 2>/dev/null || echo "    ⚠️  config_current.json not found"
cp "$OLD_DIR/disaggregated_inference/prefill_server_ollama.py" disaggregated_inference/ 2>/dev/null || echo "    ⚠️  prefill_server_ollama.py not found"
cp "$OLD_DIR/disaggregated_inference/decode_server_ollama.py" disaggregated_inference/ 2>/dev/null || echo "    ⚠️  decode_server_ollama.py not found"

# Prompts
echo "  → Prompts..."
cp "$OLD_DIR/prompt_templates/ollama/code_analysis_prompt.txt" prompt_templates/ollama/ 2>/dev/null || echo "    ⚠️  code_analysis_prompt.txt not found"
cp "$OLD_DIR/prompt_templates/ollama/feedback_prompt.txt" prompt_templates/ollama/ 2>/dev/null || echo "    ⚠️  feedback_prompt.txt not found"

# Rubrics
echo "  → Rubrics..."
cp "$OLD_DIR/rubrics/assignment_6_rubric.json" rubrics/ 2>/dev/null || echo "    ⚠️  assignment_6_rubric.json not found"
cp "$OLD_DIR/rubrics/assignment_7_rubric_v2.json" rubrics/ 2>/dev/null || echo "    ⚠️  assignment_7_rubric_v2.json not found"

# Solution notebooks
echo "  → Solution notebooks..."
cp "$OLD_DIR/data/raw/homework_lesson_6_joins_SOLUTION.ipynb" data/raw/ 2>/dev/null || echo "    ⚠️  homework_lesson_6_joins_SOLUTION.ipynb not found"
cp "$OLD_DIR/data/raw/homework_lesson_7_string_datetime_SOLUTION_v2.ipynb" data/raw/ 2>/dev/null || echo "    ⚠️  homework_lesson_7_string_datetime_SOLUTION_v2.ipynb not found"

# Sample data
echo "  → Sample data..."
cp "$OLD_DIR/data/processed/product_catalog.csv" data/processed/ 2>/dev/null || echo "    ⚠️  product_catalog.csv not found"
cp "$OLD_DIR/data/processed/transaction_log.csv" data/processed/ 2>/dev/null || echo "    ⚠️  transaction_log.csv not found"

# Requirements
echo "  → Requirements..."
cp "$OLD_DIR/requirements.txt" . 2>/dev/null || echo "    ⚠️  requirements.txt not found"

# Documentation
echo "  → Documentation..."
cp "$OLD_DIR/DISAGGREGATED_INFERENCE_SYSTEM_DOCUMENTATION.md" docs/ 2>/dev/null || echo "    ⚠️  DISAGGREGATED_INFERENCE_SYSTEM_DOCUMENTATION.md not found"
cp "$OLD_DIR/SYSTEM_DIAGRAMS.md" docs/ 2>/dev/null || echo "    ⚠️  SYSTEM_DIAGRAMS.md not found"
cp "$OLD_DIR/REPORT_FORMATTING_IMPROVEMENTS.md" docs/ 2>/dev/null || echo "    ⚠️  REPORT_FORMATTING_IMPROVEMENTS.md not found"

echo "✅ Files copied"

# Update import paths
echo ""
echo "🔧 Updating import paths..."
cat > scripts/fix_imports.py << 'PYTHON_EOF'
#!/usr/bin/env python3
"""Fix imports to use app. prefix"""
import os
import re
import glob

# Find all Python files in app/
python_files = glob.glob('app/*.py')

# Import mappings (old -> new)
import_mappings = {
    'from business_analytics_grader_v2 import': 'from app.business_analytics_grader_v2 import',
    'from grading_validator import': 'from app.grading_validator import',
    'from report_generator import': 'from app.report_generator import',
    'from ai_grader import': 'from app.ai_grader import',
    'from anonymization_utils import': 'from app.anonymization_utils import',
    'from notebook_executor import': 'from app.notebook_executor import',
    'from submission_preprocessor import': 'from app.submission_preprocessor import',
    'from prompt_manager import': 'from app.prompt_manager import',
    'from notebook_validation import': 'from app.notebook_validation import',
    'from score_validator import': 'from app.score_validator import',
    'from output_comparator import': 'from app.output_comparator import',
    'from model_status_display import': 'from app.model_status_display import',
    'from disaggregated_client import': 'from app.disaggregated_client import',
}

updated_count = 0

for filepath in python_files:
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    for old_import, new_import in import_mappings.items():
        content = content.replace(old_import, new_import)
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✅ Updated {filepath}")
        updated_count += 1

print(f"\n✅ Updated {updated_count} files")
PYTHON_EOF

chmod +x scripts/fix_imports.py
python3 scripts/fix_imports.py

# Create startup script
echo ""
echo "🚀 Creating startup script..."
cat > startup.sh << 'STARTUP_EOF'
#!/bin/bash
# AI Homework Grader - One-Click Startup

set -e

echo "🚀 AI Homework Grader - Production System"
echo "=========================================="
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This system is designed to run on macOS"
    exit 1
fi

echo "🐍 Checking Python environment..."
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ ! -f "grading_system.db" ]; then
    echo "⚠️  Database not found. You'll need to set up assignments in the web interface."
fi

if [ -f "disaggregated_inference/config_current.json" ]; then
    echo ""
    echo "🖥️  Starting disaggregated inference servers..."
    
    if [ -f "disaggregated_inference/start_all_servers.sh" ]; then
        cd disaggregated_inference
        ./start_all_servers.sh
        cd ..
        
        echo "⏳ Waiting for servers..."
        sleep 5
        
        python3 -c "
from app.disaggregated_client import DisaggregatedClient
try:
    client = DisaggregatedClient('disaggregated_inference/config_current.json')
    print('✅ Disaggregated system ready')
except Exception as e:
    print(f'⚠️  Warning: {e}')
" || echo "⚠️  Disaggregated system not available"
    fi
fi

echo ""
echo "🌐 Starting web interface..."
echo "=========================================="
echo "   URL: http://localhost:8501"
echo ""
echo "   Press Ctrl+C to stop"
echo "=========================================="
echo ""

(sleep 3 && open http://localhost:8501) &

streamlit run app/connect_web_interface.py \
    --server.port 8501 \
    --server.headless true \
    --browser.gatherUsageStats false

echo ""
echo "🛑 Shutting down..."
if [ -f "disaggregated_inference/stop_all_servers.sh" ]; then
    cd disaggregated_inference
    ./stop_all_servers.sh
    cd ..
fi
echo "✅ Shutdown complete"
STARTUP_EOF

chmod +x startup.sh
echo "✅ startup.sh created"

# Create server management scripts
echo ""
echo "🖥️  Creating server management scripts..."

cat > disaggregated_inference/start_all_servers.sh << 'START_EOF'
#!/bin/bash
echo "Starting disaggregated inference system..."

ssh dgx1 "cd /opt/inference && nohup python3 prefill_server_ollama.py --model qwen3-coder:30b --port 8000 > prefill.log 2>&1 &" 2>/dev/null || echo "⚠️  Cannot connect to DGX 1"
ssh dgx2 "cd /opt/inference && nohup python3 prefill_server_ollama.py --model gpt-oss:120b --port 8000 > prefill.log 2>&1 &" 2>/dev/null || echo "⚠️  Cannot connect to DGX 2"
ssh mac1 "cd /opt/inference && nohup python3 decode_server_ollama.py --model gpt-oss:120b --port 8001 > decode.log 2>&1 &" 2>/dev/null || echo "⚠️  Cannot connect to Mac 1"
ssh mac2 "cd /opt/inference && nohup python3 decode_server_ollama.py --model qwen3-coder:30b --port 8001 > decode.log 2>&1 &" 2>/dev/null || echo "⚠️  Cannot connect to Mac 2"

echo "✅ Server startup commands sent"
START_EOF

cat > disaggregated_inference/stop_all_servers.sh << 'STOP_EOF'
#!/bin/bash
echo "Stopping disaggregated inference system..."

ssh dgx1 "pkill -f prefill_server_ollama.py" 2>/dev/null || true
ssh dgx2 "pkill -f prefill_server_ollama.py" 2>/dev/null || true
ssh mac1 "pkill -f decode_server_ollama.py" 2>/dev/null || true
ssh mac2 "pkill -f decode_server_ollama.py" 2>/dev/null || true

echo "✅ All servers stopped"
STOP_EOF

cat > disaggregated_inference/check_status.sh << 'STATUS_EOF'
#!/bin/bash
echo "Checking server status..."
echo ""

check_server() {
    echo "$1:"
    curl -s --connect-timeout 2 "$2/health" | python3 -m json.tool 2>/dev/null && echo "✅ Online" || echo "❌ Offline"
    echo ""
}

check_server "DGX Spark 1 (Qwen prefill)" "http://169.254.150.103:8000"
check_server "DGX Spark 2 (GPT-OSS prefill)" "http://169.254.150.104:8000"
check_server "Mac Studio 1 (GPT-OSS decode)" "http://169.254.150.101:8001"
check_server "Mac Studio 2 (Qwen decode)" "http://169.254.150.102:8001"
STATUS_EOF

chmod +x disaggregated_inference/*.sh
echo "✅ Server scripts created"

# Create README
echo ""
echo "📝 Creating README..."
cat > README.md << 'README_EOF'
# AI Homework Grader - Production System

Automated grading system for business analytics homework using disaggregated inference.

## Quick Start

```bash
./startup.sh
```

The system will automatically:
- Set up Python environment
- Install dependencies
- Start inference servers
- Launch web interface at http://localhost:8501

## Architecture

- **DGX Sparks**: Fast parallel prefill (H100 GPUs)
- **Mac Studios**: Efficient decode (M3/M4 chips)
- **Orchestrator**: Coordinates distributed inference
- **Web Interface**: Streamlit-based UI

## Documentation

See `docs/` for detailed documentation:
- Disaggregated inference architecture
- System diagrams
- Report formatting guide

## Maintenance

```bash
# Check server status
cd disaggregated_inference && ./check_status.sh

# Restart servers
cd disaggregated_inference && ./stop_all_servers.sh && ./start_all_servers.sh
```

## License

MIT License
README_EOF

echo "✅ README created"

# Initialize Git
echo ""
echo "📦 Initializing Git repository..."
git init
git branch -M main
git add .
git commit -m "Initial production release

- Clean directory structure
- One-click startup script
- Disaggregated inference system
- 4-layer validation grading
- PDF report generation
- Streamlit web interface"

echo "✅ Git repository initialized"

# Summary
echo ""
echo "=========================================="
echo "✅ Production version created successfully!"
echo "=========================================="
echo ""
echo "📂 Location: $NEW_DIR"
echo ""
echo "📝 Next steps:"
echo "1. cd $NEW_DIR"
echo "2. Test: ./startup.sh"
echo "3. Create GitHub repo: https://github.com/new"
echo "4. Push:"
echo "   git remote add origin git@github.com:YOUR_USERNAME/ai-homework-grader-production.git"
echo "   git push -u origin main"
echo ""
echo "🎉 Done!"
