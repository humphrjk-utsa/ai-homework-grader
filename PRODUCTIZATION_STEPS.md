# AI Homework Grader - Production Setup Guide

## Step-by-Step Productization

### Step 1: Create New Production Folder

```bash
# Navigate to parent directory
cd ~/GitHub

# Create new production folder
mkdir ai-homework-grader-production
cd ai-homework-grader-production

# Initialize Git
git init
git branch -M main
```

### Step 2: Create Clean Directory Structure

```bash
# Create directory structure
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

# Create .gitignore
cat > .gitignore << 'EOF'
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
.DS_Store

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
EOF
```

### Step 3: Copy Production Files

```bash
# From the old project directory
OLD_DIR=~/GitHub/ai-homework-grader-clean
NEW_DIR=~/GitHub/ai-homework-grader-production

# Copy core application files
cp $OLD_DIR/connect_web_interface.py $NEW_DIR/app/
cp $OLD_DIR/business_analytics_grader_v2.py $NEW_DIR/app/
cp $OLD_DIR/disaggregated_client.py $NEW_DIR/app/
cp $OLD_DIR/prompt_manager.py $NEW_DIR/app/
cp $OLD_DIR/grading_validator.py $NEW_DIR/app/
cp $OLD_DIR/report_generator.py $NEW_DIR/app/
cp $OLD_DIR/score_validator.py $NEW_DIR/app/
cp $OLD_DIR/notebook_executor.py $NEW_DIR/app/
cp $OLD_DIR/submission_preprocessor.py $NEW_DIR/app/
cp $OLD_DIR/anonymization_utils.py $NEW_DIR/app/
cp $OLD_DIR/model_status_display.py $NEW_DIR/app/
cp $OLD_DIR/notebook_validation.py $NEW_DIR/app/
cp $OLD_DIR/output_comparator.py $NEW_DIR/app/
cp $OLD_DIR/ai_grader.py $NEW_DIR/app/

# Copy validators
cp -r $OLD_DIR/validators/* $NEW_DIR/validators/

# Copy disaggregated inference
cp $OLD_DIR/disaggregated_inference/config_current.json $NEW_DIR/disaggregated_inference/
cp $OLD_DIR/disaggregated_inference/prefill_server_ollama.py $NEW_DIR/disaggregated_inference/
cp $OLD_DIR/disaggregated_inference/decode_server_ollama.py $NEW_DIR/disaggregated_inference/

# Copy prompts
cp $OLD_DIR/prompt_templates/ollama/code_analysis_prompt.txt $NEW_DIR/prompt_templates/ollama/
cp $OLD_DIR/prompt_templates/ollama/feedback_prompt.txt $NEW_DIR/prompt_templates/ollama/

# Copy rubrics
cp $OLD_DIR/rubrics/assignment_6_rubric.json $NEW_DIR/rubrics/
cp $OLD_DIR/rubrics/assignment_7_rubric_v2.json $NEW_DIR/rubrics/

# Copy solution notebooks
cp $OLD_DIR/data/raw/homework_lesson_6_joins_SOLUTION.ipynb $NEW_DIR/data/raw/
cp $OLD_DIR/data/raw/homework_lesson_7_string_datetime_SOLUTION_v2.ipynb $NEW_DIR/data/raw/

# Copy sample data files
cp $OLD_DIR/data/processed/product_catalog.csv $NEW_DIR/data/processed/
cp $OLD_DIR/data/processed/transaction_log.csv $NEW_DIR/data/processed/

# Copy requirements
cp $OLD_DIR/requirements.txt $NEW_DIR/

# Copy documentation
cp $OLD_DIR/DISAGGREGATED_INFERENCE_SYSTEM_DOCUMENTATION.md $NEW_DIR/docs/
cp $OLD_DIR/SYSTEM_DIAGRAMS.md $NEW_DIR/docs/
cp $OLD_DIR/REPORT_FORMATTING_IMPROVEMENTS.md $NEW_DIR/docs/
```

### Step 4: Update Import Paths

All Python files in `app/` need to import from `app.` prefix:

```python
# OLD (in root):
from business_analytics_grader_v2 import BusinessAnalyticsGraderV2

# NEW (in app/):
from app.business_analytics_grader_v2 import BusinessAnalyticsGraderV2
```

Create a script to fix imports:

```bash
cd $NEW_DIR

# Create import fixer script
cat > scripts/fix_imports.py << 'EOF'
#!/usr/bin/env python3
"""Fix imports to use app. prefix"""
import os
import re

# Files to update
files_to_update = [
    'app/connect_web_interface.py',
    'app/business_analytics_grader_v2.py',
    'app/disaggregated_client.py',
]

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

for filepath in files_to_update:
    if not os.path.exists(filepath):
        print(f"⚠️  Skipping {filepath} (not found)")
        continue
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    for old_import, new_import in import_mappings.items():
        content = content.replace(old_import, new_import)
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Updated {filepath}")
    else:
        print(f"⏭️  No changes needed for {filepath}")

print("\n✅ Import paths updated!")
EOF

chmod +x scripts/fix_imports.py
python3 scripts/fix_imports.py
```

### Step 5: Create Startup Script

```bash
cd $NEW_DIR

cat > startup.sh << 'EOF'
#!/bin/bash
# AI Homework Grader - One-Click Startup
# Starts all servers and opens the web interface

set -e  # Exit on error

echo "🚀 AI Homework Grader - Production System"
echo "=========================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if running on Mac
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This system is designed to run on macOS"
    echo "   For DGX servers, use: disaggregated_inference/start_prefill_server.sh"
    exit 1
fi

# 1. Check Python environment
echo "🐍 Checking Python environment..."
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# 2. Install/update dependencies
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 3. Check database
if [ ! -f "grading_system.db" ]; then
    echo "⚠️  Database not found. Creating new database..."
    echo "   You'll need to set up assignments and students in the web interface."
fi

# 4. Start disaggregated servers (if configured)
if [ -f "disaggregated_inference/config_current.json" ]; then
    echo ""
    echo "🖥️  Starting disaggregated inference servers..."
    
    # Check if start script exists
    if [ -f "disaggregated_inference/start_all_servers.sh" ]; then
        cd disaggregated_inference
        ./start_all_servers.sh
        cd ..
        
        echo "⏳ Waiting for servers to initialize..."
        sleep 5
        
        # Check server health
        echo "🏥 Checking server health..."
        python3 -c "
from app.disaggregated_client import DisaggregatedClient
try:
    client = DisaggregatedClient('disaggregated_inference/config_current.json')
    print('✅ Disaggregated system ready')
    print('   DGX Sparks: Prefill servers')
    print('   Mac Studios: Decode servers')
except Exception as e:
    print(f'⚠️  Warning: {e}')
    print('   System will use fallback mode if needed')
" || echo "⚠️  Disaggregated system not available - will use fallback"
    else
        echo "⚠️  Server start script not found"
        echo "   Disaggregated system will not be available"
    fi
else
    echo "⚠️  Disaggregated inference not configured"
    echo "   System will use local Ollama if available"
fi

# 5. Start Streamlit app
echo ""
echo "🌐 Starting web interface..."
echo "=========================================="
echo "   URL: http://localhost:8501"
echo ""
echo "   Press Ctrl+C to stop all services"
echo "=========================================="
echo ""

# Open browser after 3 seconds
(sleep 3 && open http://localhost:8501) &

# Start Streamlit (this blocks until Ctrl+C)
streamlit run app/connect_web_interface.py \
    --server.port 8501 \
    --server.headless true \
    --browser.gatherUsageStats false

# Cleanup on exit
echo ""
echo "🛑 Shutting down..."
if [ -f "disaggregated_inference/stop_all_servers.sh" ]; then
    cd disaggregated_inference
    ./stop_all_servers.sh
    cd ..
fi
echo "✅ Shutdown complete"
EOF

chmod +x startup.sh
```

### Step 6: Create Server Management Scripts

```bash
cd $NEW_DIR/disaggregated_inference

# Start all servers
cat > start_all_servers.sh << 'EOF'
#!/bin/bash
# Start all disaggregated inference servers

echo "Starting disaggregated inference system..."

# Check if SSH keys are set up
if ! ssh -o BatchMode=yes -o ConnectTimeout=5 dgx1 exit 2>/dev/null; then
    echo "⚠️  Cannot connect to DGX servers via SSH"
    echo "   Make sure SSH keys are configured"
    exit 1
fi

# Start DGX prefill servers (via SSH)
echo "🖥️  Starting DGX Spark 1 (Qwen prefill)..."
ssh dgx1 "cd /opt/inference && nohup python3 prefill_server_ollama.py --model qwen3-coder:30b --port 8000 > prefill.log 2>&1 &" || echo "⚠️  Failed to start DGX 1"

echo "🖥️  Starting DGX Spark 2 (GPT-OSS prefill)..."
ssh dgx2 "cd /opt/inference && nohup python3 prefill_server_ollama.py --model gpt-oss:120b --port 8000 > prefill.log 2>&1 &" || echo "⚠️  Failed to start DGX 2"

# Start Mac decode servers
echo "🍎 Starting Mac Studio 1 (GPT-OSS decode)..."
ssh mac1 "cd /opt/inference && nohup python3 decode_server_ollama.py --model gpt-oss:120b --port 8001 > decode.log 2>&1 &" || echo "⚠️  Failed to start Mac 1"

echo "🍎 Starting Mac Studio 2 (Qwen decode)..."
ssh mac2 "cd /opt/inference && nohup python3 decode_server_ollama.py --model qwen3-coder:30b --port 8001 > decode.log 2>&1 &" || echo "⚠️  Failed to start Mac 2"

echo "✅ Server startup commands sent"
echo "   Use ./check_status.sh to verify"
EOF

# Stop all servers
cat > stop_all_servers.sh << 'EOF'
#!/bin/bash
# Stop all disaggregated inference servers

echo "Stopping disaggregated inference system..."

# Stop DGX servers
ssh dgx1 "pkill -f prefill_server_ollama.py" 2>/dev/null || true
ssh dgx2 "pkill -f prefill_server_ollama.py" 2>/dev/null || true

# Stop Mac servers
ssh mac1 "pkill -f decode_server_ollama.py" 2>/dev/null || true
ssh mac2 "pkill -f decode_server_ollama.py" 2>/dev/null || true

echo "✅ All servers stopped"
EOF

# Check status
cat > check_status.sh << 'EOF'
#!/bin/bash
# Check status of all servers

echo "Checking server status..."
echo ""

check_server() {
    local name=$1
    local url=$2
    
    echo "$name:"
    if curl -s --connect-timeout 2 "$url/health" | python3 -m json.tool 2>/dev/null; then
        echo "✅ Online"
    else
        echo "❌ Offline"
    fi
    echo ""
}

check_server "DGX Spark 1 (Qwen prefill)" "http://169.254.150.103:8000"
check_server "DGX Spark 2 (GPT-OSS prefill)" "http://169.254.150.104:8000"
check_server "Mac Studio 1 (GPT-OSS decode)" "http://169.254.150.101:8001"
check_server "Mac Studio 2 (Qwen decode)" "http://169.254.150.102:8001"
EOF

# Make all scripts executable
chmod +x start_all_servers.sh
chmod +x stop_all_servers.sh
chmod +x check_status.sh
```

### Step 7: Create README

```bash
cd $NEW_DIR

cat > README.md << 'EOF'
# AI Homework Grader - Production System

Automated grading system for business analytics homework using disaggregated inference across DGX Sparks and Mac Studios.

## Quick Start

```bash
./startup.sh
```

That's it! The system will:
- ✅ Set up Python environment
- ✅ Install dependencies
- ✅ Start all inference servers
- ✅ Launch web interface
- ✅ Open browser automatically

## System Architecture

- **DGX Sparks**: Fast parallel prefill (prompt processing)
- **Mac Studios**: Efficient sequential decode (token generation)
- **Orchestrator**: Coordinates distributed inference
- **Web Interface**: Streamlit-based grading UI

## Components

### Core Application (`app/`)
- `connect_web_interface.py` - Main Streamlit UI
- `business_analytics_grader_v2.py` - 4-layer validation grading engine
- `disaggregated_client.py` - Distributed inference orchestrator

### Validators (`validators/`)
- `rubric_driven_validator.py` - Generic rubric-based validation
- `smart_output_validator.py` - Output comparison with solutions

### Inference Servers (`disaggregated_inference/`)
- `prefill_server_ollama.py` - DGX prefill server
- `decode_server_ollama.py` - Mac decode server
- `config_current.json` - Server configuration

## Requirements

- Python 3.10+
- macOS (for orchestrator)
- DGX Sparks with H100 GPUs (for prefill)
- Mac Studios with M3/M4 (for decode)
- Ollama installed on all machines
- SSH access configured

## Documentation

See `docs/` folder for:
- Disaggregated inference architecture
- System diagrams
- Report formatting guide

## Maintenance

```bash
# Check server status
cd disaggregated_inference && ./check_status.sh

# Restart servers
cd disaggregated_inference && ./stop_all_servers.sh && ./start_all_servers.sh

# View logs
tail -f logs/*.log
```

## License

MIT License - See LICENSE file
EOF
```

### Step 8: Initialize Git and Push to GitHub

```bash
cd $NEW_DIR

# Initialize Git
git init
git branch -M main

# Add all files
git add .

# Initial commit
git commit -m "Initial production release

- Clean directory structure
- One-click startup script
- Disaggregated inference system
- 4-layer validation grading
- PDF report generation
- Streamlit web interface"

# Create GitHub repo (you'll need to do this manually on GitHub)
echo ""
echo "📝 Next steps:"
echo "1. Go to https://github.com/new"
echo "2. Create repo: ai-homework-grader-production"
echo "3. Run these commands:"
echo ""
echo "   git remote add origin git@github.com:YOUR_USERNAME/ai-homework-grader-production.git"
echo "   git push -u origin main"
echo ""
```

### Step 9: Test the System

```bash
cd $NEW_DIR

# Test startup
./startup.sh

# In another terminal, check servers
cd disaggregated_inference
./check_status.sh

# Test grading a submission through the web interface
# Navigate to http://localhost:8501
```

## Summary

After following these steps, you'll have:

✅ Clean production folder: `ai-homework-grader-production/`
✅ Organized structure: Only 20 core files vs 100+ in old repo
✅ One-click startup: `./startup.sh`
✅ Git repository: Ready to push to GitHub
✅ Documentation: All docs in `docs/` folder
✅ Server management: Easy start/stop/status scripts

## File Count Comparison

**Old repo**: 100+ files in root directory
**New repo**: 
- 20 core files in `app/`
- 3 validators
- 3 server files
- 2 prompts
- Clean, organized, professional

Ready to execute? Let me know and I'll create the migration script!
