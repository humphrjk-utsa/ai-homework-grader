# Production System Audit & Productization Plan

## Current State Analysis

### Core Production Files (KEEP - ACTIVELY USED)

#### Main Application
- `connect_web_interface.py` - Main Streamlit web interface
- `business_analytics_grader_v2.py` - Core grading engine with 4-layer validation
- `disaggregated_client.py` - Orchestrator for DGX+Mac inference

#### Grading Components
- `prompt_manager.py` - Manages Ollama prompts
- `grading_validator.py` - Validates scoring calculations
- `report_generator.py` - Generates PDF reports
- `score_validator.py` - Score validation logic
- `notebook_executor.py` - Executes notebooks if needed
- `submission_preprocessor.py` - Cleans/normalizes submissions
- `anonymization_utils.py` - Anonymizes student names

#### Validators (validators/)
- `validators/rubric_driven_validator.py` - Generic rubric-based validation
- `validators/assignment_6_systematic_validator.py` - Assignment 6 specific
- `validators/smart_output_validator.py` - Output comparison with solution

#### Legacy Validators (KEEP for backward compatibility)
- `notebook_validation.py` - Legacy validator (fallback)
- `output_comparator.py` - Legacy output comparison

#### Prompts (prompt_templates/ollama/)
- `prompt_templates/ollama/code_analysis_prompt.txt` - Qwen code analysis
- `prompt_templates/ollama/feedback_prompt.txt` - GPT-OSS feedback generation

#### Disaggregated Inference (disaggregated_inference/)
- `disaggregated_inference/prefill_server_ollama.py` - DGX prefill server
- `disaggregated_inference/decode_server_ollama.py` - Mac decode server
- `disaggregated_inference/config_current.json` - Server configuration

#### Data & Configuration
- `grading_system.db` - SQLite database (assignments, submissions, students)
- `rubrics/*.json` - Assignment rubrics
- `data/raw/*.ipynb` - Solution notebooks
- `requirements.txt` - Python dependencies

#### Model Status
- `model_status_display.py` - Shows AI model status in UI

---

### Legacy/Experimental Files (ARCHIVE OR DELETE)

#### Old Grader Versions
- `business_analytics_grader_old.py` ❌ DELETE
- `business_analytics_grader_original.py` ❌ DELETE
- `business_analytics_grader_v2_broken.py` ❌ DELETE
- `business_analytics_grader_v2_master.py` ❌ DELETE
- `business_analytics_grader.py` ❌ DELETE
- `ai_grader.py` ⚠️ KEEP (has filter_ai_feedback_for_storage function)

#### Test Files
- `test_*.py` (all test files) 📦 MOVE TO tests/
- `grade_with_systematic_validator.py` 📦 MOVE TO tests/
- `regrade_with_new_validator.py` 📦 MOVE TO tests/

#### Documentation (Keep but organize)
- `*.md` files 📦 MOVE TO docs/
- Keep only `README.md` in root

#### Unused Interfaces
- `grading_interface.py` ❌ DELETE (replaced by connect_web_interface.py)
- `app.py` ❌ DELETE (old interface)
- `training_interface.py` ❌ DELETE
- `enhanced_training_interface.py` ❌ DELETE
- `modern_training_interface.py` ❌ DELETE
- `enhanced_training_page.py` ❌ DELETE

#### Unused Utilities
- `alternative_approaches.py` ❌ DELETE
- `assignment_editor.py` ❌ DELETE
- `assignment_manager.py` ❌ DELETE
- `assignment_matcher.py` ❌ DELETE
- `assignment_setup_helper.py` ❌ DELETE
- `correction_analyzer.py` ❌ DELETE
- `correction_helpers.py` ❌ DELETE
- `create_solution_notebook.py` ❌ DELETE
- `create_solution.py` ❌ DELETE
- `migration_helper.py` ❌ DELETE
- `rubric_manager.py` ❌ DELETE
- `server_manager.py` ❌ DELETE
- `unified_model_interface.py` ❌ DELETE

#### Unused Monitoring
- `monitor_dashboard_full.py` ❌ DELETE
- `monitor_dashboard.py` ⚠️ KEEP (might be used)
- `monitor_app.py` ⚠️ KEEP (might be used)
- `performance_logger.py` ❌ DELETE

#### Unused Databases
- `enhanced_training.db` ❌ DELETE
- `grading_database.db` ❌ DELETE (use grading_system.db)

#### Shell Scripts (Organize)
- `clean_restart.sh` 📦 MOVE TO scripts/
- `cleanup_root_directory.sh` 📦 MOVE TO scripts/
- `quick_restart.sh` 📦 MOVE TO scripts/
- `safe_cleanup.sh` 📦 MOVE TO scripts/
- `restart_oss_server.sh` 📦 MOVE TO scripts/
- `monitor_macs.sh` 📦 MOVE TO scripts/

#### Unused Config
- `distributed_config.json.mlx_not_used` ❌ DELETE
- `ollama_servers.json` ❌ DELETE
- `server_config.json` ❌ DELETE
- `model_config.py` ❌ DELETE

---

## Proposed Clean Structure

```
ai-homework-grader/
├── README.md                          # Main documentation
├── requirements.txt                   # Python dependencies
├── startup.sh                         # ONE-CLICK STARTUP SCRIPT
├── grading_system.db                  # Main database
│
├── app/                               # Main application
│   ├── connect_web_interface.py       # Streamlit UI
│   ├── business_analytics_grader_v2.py
│   ├── disaggregated_client.py
│   ├── prompt_manager.py
│   ├── grading_validator.py
│   ├── report_generator.py
│   ├── score_validator.py
│   ├── notebook_executor.py
│   ├── submission_preprocessor.py
│   ├── anonymization_utils.py
│   ├── model_status_display.py
│   ├── notebook_validation.py         # Legacy fallback
│   ├── output_comparator.py           # Legacy fallback
│   └── ai_grader.py                   # Helper functions
│
├── validators/                        # Validation modules
│   ├── rubric_driven_validator.py
│   ├── assignment_6_systematic_validator.py
│   └── smart_output_validator.py
│
├── disaggregated_inference/           # Distributed inference
│   ├── config_current.json
│   ├── prefill_server_ollama.py
│   ├── decode_server_ollama.py
│   ├── start_all_servers.sh           # Start DGX + Mac servers
│   └── stop_all_servers.sh
│
├── prompt_templates/                  # AI prompts
│   └── ollama/
│       ├── code_analysis_prompt.txt
│       └── feedback_prompt.txt
│
├── rubrics/                           # Assignment rubrics
│   ├── assignment_6_rubric.json
│   └── assignment_7_rubric_v2.json
│
├── data/                              # Data files
│   ├── raw/                           # Solution notebooks
│   └── processed/                     # Processed data
│
├── reports/                           # Generated PDF reports
│   ├── Assignment_6/
│   └── Assignment_7/
│
├── submissions/                       # Student submissions
│
├── docs/                              # Documentation
│   ├── DISAGGREGATED_INFERENCE_SYSTEM_DOCUMENTATION.md
│   ├── SYSTEM_DIAGRAMS.md
│   ├── REPORT_FORMATTING_IMPROVEMENTS.md
│   └── *.md                           # All other docs
│
├── scripts/                           # Utility scripts
│   ├── clean_restart.sh
│   ├── quick_restart.sh
│   └── monitor_macs.sh
│
├── tests/                             # Test files
│   ├── test_*.py
│   └── grade_with_systematic_validator.py
│
└── archive/                           # Old/unused files
    ├── old_graders/
    ├── old_interfaces/
    └── old_utilities/
```

---

## ONE-CLICK STARTUP SYSTEM

### startup.sh (Main Launcher)

```bash
#!/bin/bash
# AI Homework Grader - One-Click Startup
# Starts all servers and opens the web interface

set -e  # Exit on error

echo "🚀 Starting AI Homework Grader System..."
echo ""

# Check if running on Mac (orchestrator)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📍 Detected Mac - Starting as Orchestrator"
    
    # 1. Check Python environment
    if [ ! -d ".venv" ]; then
        echo "❌ Virtual environment not found. Run: python3 -m venv .venv"
        exit 1
    fi
    
    source .venv/bin/activate
    
    # 2. Check dependencies
    echo "📦 Checking dependencies..."
    pip install -q -r requirements.txt
    
    # 3. Start disaggregated servers (DGX + Mac)
    echo "🖥️  Starting disaggregated inference servers..."
    cd disaggregated_inference
    ./start_all_servers.sh
    cd ..
    
    # Wait for servers to be ready
    echo "⏳ Waiting for servers to initialize..."
    sleep 5
    
    # 4. Check server health
    echo "🏥 Checking server health..."
    python3 -c "
from disaggregated_client import DisaggregatedClient
try:
    client = DisaggregatedClient()
    print('✅ Disaggregated system ready')
except Exception as e:
    print(f'⚠️  Warning: {e}')
    print('   System will use fallback mode')
"
    
    # 5. Start Streamlit app
    echo ""
    echo "🌐 Starting web interface..."
    echo "   URL: http://localhost:8501"
    echo ""
    echo "Press Ctrl+C to stop all services"
    echo ""
    
    # Open browser after 2 seconds
    (sleep 2 && open http://localhost:8501) &
    
    # Start Streamlit
    streamlit run app/connect_web_interface.py --server.port 8501
    
else
    echo "❌ This script should be run on the Mac orchestrator"
    echo "   For DGX servers, use: disaggregated_inference/start_prefill_server.sh"
    exit 1
fi
```

### disaggregated_inference/start_all_servers.sh

```bash
#!/bin/bash
# Start all disaggregated inference servers

echo "Starting disaggregated inference system..."

# Start DGX prefill servers (via SSH)
echo "🖥️  Starting DGX Spark 1 (Qwen prefill)..."
ssh dgx1 "cd /opt/inference && nohup python3 prefill_server_ollama.py --model qwen3-coder:30b --port 8000 > prefill.log 2>&1 &"

echo "🖥️  Starting DGX Spark 2 (GPT-OSS prefill)..."
ssh dgx2 "cd /opt/inference && nohup python3 prefill_server_ollama.py --model gpt-oss:120b --port 8000 > prefill.log 2>&1 &"

# Start Mac decode servers (local)
echo "🍎 Starting Mac Studio 1 (GPT-OSS decode)..."
ssh mac1 "cd /opt/inference && nohup python3 decode_server_ollama.py --model gpt-oss:120b --port 8001 > decode.log 2>&1 &"

echo "🍎 Starting Mac Studio 2 (Qwen decode)..."
ssh mac2 "cd /opt/inference && nohup python3 decode_server_ollama.py --model qwen3-coder:30b --port 8001 > decode.log 2>&1 &"

echo "✅ All servers started"
echo "   Check status: ./check_status.sh"
```

### disaggregated_inference/stop_all_servers.sh

```bash
#!/bin/bash
# Stop all disaggregated inference servers

echo "Stopping disaggregated inference system..."

# Stop DGX servers
ssh dgx1 "pkill -f prefill_server_ollama.py"
ssh dgx2 "pkill -f prefill_server_ollama.py"

# Stop Mac servers
ssh mac1 "pkill -f decode_server_ollama.py"
ssh mac2 "pkill -f decode_server_ollama.py"

echo "✅ All servers stopped"
```

### disaggregated_inference/check_status.sh

```bash
#!/bin/bash
# Check status of all servers

echo "Checking server status..."
echo ""

# Check DGX 1
echo "DGX Spark 1 (Qwen prefill):"
curl -s http://169.254.150.103:8000/health | python3 -m json.tool || echo "❌ Offline"
echo ""

# Check DGX 2
echo "DGX Spark 2 (GPT-OSS prefill):"
curl -s http://169.254.150.104:8000/health | python3 -m json.tool || echo "❌ Offline"
echo ""

# Check Mac 1
echo "Mac Studio 1 (GPT-OSS decode):"
curl -s http://169.254.150.101:8001/health | python3 -m json.tool || echo "❌ Offline"
echo ""

# Check Mac 2
echo "Mac Studio 2 (Qwen decode):"
curl -s http://169.254.150.102:8001/health | python3 -m json.tool || echo "❌ Offline"
```

---

## Migration Steps

### Phase 1: Organize (No Breaking Changes)
1. Create new directory structure
2. Move files to appropriate locations
3. Update imports in moved files
4. Test that everything still works

### Phase 2: Create Startup Scripts
1. Create `startup.sh` in root
2. Create server management scripts in `disaggregated_inference/`
3. Make all scripts executable
4. Test startup process

### Phase 3: Clean Up
1. Move old files to `archive/`
2. Delete truly unused files
3. Update documentation
4. Create clean README.md

### Phase 4: Productize
1. Add error handling to startup script
2. Add health checks
3. Add automatic recovery
4. Create systemd services (optional)

---

## Usage After Productization

### For Daily Use:
```bash
# Start everything
./startup.sh

# That's it! Browser opens automatically to http://localhost:8501
```

### For Maintenance:
```bash
# Check server status
cd disaggregated_inference && ./check_status.sh

# Restart servers
cd disaggregated_inference && ./stop_all_servers.sh && ./start_all_servers.sh

# View logs
tail -f disaggregated_inference/logs/*.log
```

### For Development:
```bash
# Run tests
cd tests && python3 -m pytest

# Grade single submission (testing)
python3 tests/test_grade_marc.py
```

---

## Benefits

1. **One-Click Startup**: Just run `./startup.sh`
2. **Clean Structure**: Easy to navigate and understand
3. **Maintainable**: Clear separation of concerns
4. **Documented**: Each component has clear purpose
5. **Testable**: Tests separated from production code
6. **Scalable**: Easy to add new features

---

## Next Steps

1. **Review this plan** - Confirm what to keep/delete
2. **Create migration script** - Automate the reorganization
3. **Test migration** - Ensure nothing breaks
4. **Create startup scripts** - Implement one-click startup
5. **Document** - Update README with new structure

Would you like me to proceed with any of these phases?
