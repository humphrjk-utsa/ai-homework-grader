# Root Directory Files Analysis

## 📊 Current State: 117 Files in Root

This is way too many! Let's identify what's actually needed.

---

## ✅ ESSENTIAL FILES (Must Keep - ~25 files)

### Core Application (7 files)
```
app.py                          # Main Streamlit application
business_analytics_grader.py    # Core grading engine
gpt_oss_server_working.py      # GPT-OSS server (Mac 1)
qwen_8bit_server.py            # Qwen server (Mac 2)
server_manager.py              # Server management
distributed_config.json        # Server configuration
requirements.txt               # Python dependencies
```

### Web Interface Components (8 files)
```
assignment_manager.py          # Assignment creation/upload
assignment_editor.py           # Assignment editing
connect_web_interface.py       # Grading page
grading_interface.py           # Results viewing
training_interface.py          # AI training
enhanced_training_page.py      # Enhanced training UI
prompt_manager.py              # Prompt management
model_status_display.py        # Server status
```

### Core Support (10 files)
```
submission_preprocessor.py     # Cleans submissions
report_generator.py            # PDF reports
assignment_matcher.py          # Matches assignments
grading_validator.py           # Validates grades
correction_analyzer.py         # Analyzes corrections
anonymization_utils.py         # Anonymizes data
notebook_validation.py         # Validates notebooks
output_verifier.py             # Verifies outputs
ai_grader.py                   # AI grading logic
model_config.py                # Model configuration
```

---

## 🗑️ CAN DELETE - Deployment Scripts (~20 files)

These were for one-time setup and are no longer needed:

```bash
# Mac deployment (already deployed)
deploy_mac1.sh
deploy_mac2.sh
deploy_to_headless_mac.py
copy_gemma_only.sh
copy_models_to_mac2.sh
boost_transfer_rate.sh

# Installation (already installed)
install.sh
install_hf_cli_mac2.sh
fix_hf_cli_path.sh
clear_locks_and_download.sh

# Model downloads (already downloaded)
download_qwen_8bit.sh
check_qwen_model.sh

# Status checks (have better monitoring)
check_mac2_memory.sh
check_mac2_status.sh
check_status.sh

# Old cleanup scripts
cleanup_main_directory.sh
```

---

## 🗑️ CAN DELETE - Old/Duplicate Versions (~15 files)

```bash
# Old training interfaces
dual_panel_layout.py
dual_panel_training_interface.py
integrated_dual_panel_system.py
enhanced_training_database.py
enhanced_training_integration.py
enhanced_training_interface.py

# Old helpers
assignment_setup_helper.py
correction_helpers.py

# Debug scripts
debug_code_suggestions.py
create_assignment3_solution.py
```

---

## 🗑️ CAN DELETE - Documentation Duplicates (~30 files)

Keep only the most recent/relevant docs:

```bash
# Old setup guides (info now in main docs)
ASSIGNMENT_3_SETUP_GUIDE.md
ASSIGNMENT_5_GRADING_SETUP.md
GIT_SETUP_COMMANDS.md
HEADLESS_DEPLOYMENT_GUIDE.md
LAUNCHER_README.md

# Old architecture docs (consolidated)
DATA_CONSISTENCY_ARCHITECTURE.md

# Homework-specific docs (move to docs/)
HOMEWORK_8_GAPS_AND_FIXES.md
HOMEWORK_8_MIDTERM_COVERAGE.md

# Performance docs (keep recent ones)
LARGE_FILE_SOLUTION.md  # Keep
PERFORMANCE_*.md        # Keep recent ones
```

---

## 📁 SHOULD MOVE TO SUBDIRECTORIES

### Move to `scripts/` folder:
```bash
# Monitoring scripts
monitor_dashboard.py
monitor_dashboard_full.py
monitor_app.py
monitor_macs.sh
performance_logger.py
analyze_performance_logs.py

# Restart scripts
restart_servers.sh
RESTART_NOW.sh
restart_qwen.sh
swap_models.sh
```

### Move to `docs/` folder:
```bash
# All .md files except README.md
SYSTEM_ARCHITECTURE.md
DOCKER_DEPLOYMENT.md
SAFE_CLEANUP_PLAN.md
etc.
```

### Move to `tests/` folder:
```bash
# Test files
francisco_feedback_test.py
test_grading_system.py
test_distributed_grading.py
test_mlx_servers.py
verify_verbose_feedback.py
```

---

## 🎯 RECOMMENDED CLEANUP ACTIONS

### Phase 1: Safe Deletions (Do Now)
```bash
# Delete deployment scripts (already deployed)
rm -f deploy_mac*.sh copy_*.sh boost_transfer_rate.sh
rm -f install*.sh fix_hf_cli_path.sh clear_locks_and_download.sh
rm -f download_qwen_8bit.sh check_qwen_model.sh
rm -f check_mac2_*.sh check_status.sh cleanup_main_directory.sh

# Delete old versions
rm -f dual_panel_*.py integrated_dual_panel_system.py
rm -f enhanced_training_database.py enhanced_training_integration.py
rm -f enhanced_training_interface.py
rm -f assignment_setup_helper.py correction_helpers.py
rm -f debug_code_suggestions.py create_assignment3_solution.py

# Delete old docs
rm -f ASSIGNMENT_3_SETUP_GUIDE.md ASSIGNMENT_5_GRADING_SETUP.md
rm -f GIT_SETUP_COMMANDS.md HEADLESS_DEPLOYMENT_GUIDE.md
rm -f LAUNCHER_README.md DATA_CONSISTENCY_ARCHITECTURE.md
rm -f HOMEWORK_8_GAPS_AND_FIXES.md HOMEWORK_8_MIDTERM_COVERAGE.md
```

**Expected result:** Remove ~65 files

### Phase 2: Organize (Do Next)
```bash
# Create subdirectories
mkdir -p scripts tests docs

# Move monitoring scripts
mv monitor_*.py performance_logger.py analyze_performance_logs.py scripts/
mv monitor_macs.sh scripts/

# Move restart scripts
mv restart_*.sh RESTART_NOW.sh swap_models.sh scripts/

# Move test files
mv *_test.py test_*.py verify_*.py tests/

# Move documentation
mv *.md docs/
mv docs/README.md .  # Keep README in root
```

**Expected result:** Organized structure

---

## 📊 BEFORE vs AFTER

### Before:
```
Root directory: 117 files
- 60 Python files
- 30 Shell scripts
- 27 Markdown files
```

### After Phase 1 (Cleanup):
```
Root directory: ~52 files
- 35 Python files
- 5 Shell scripts
- 12 Markdown files
```

### After Phase 2 (Organization):
```
Root directory: ~25 essential files
scripts/: ~15 files
tests/: ~10 files
docs/: ~25 files
```

---

## ✅ FINAL ROOT DIRECTORY (Goal)

```
ai-homework-grader-clean/
├── app.py                          # Main app
├── business_analytics_grader.py    # Core grading
├── gpt_oss_server_working.py      # Server 1
├── qwen_8bit_server.py            # Server 2
├── server_manager.py              # Server management
├── distributed_config.json        # Config
├── requirements.txt               # Dependencies
├── README.md                      # Main readme
│
├── assignment_manager.py          # Web components
├── assignment_editor.py
├── connect_web_interface.py
├── grading_interface.py
├── training_interface.py
├── enhanced_training_page.py
├── prompt_manager.py
├── model_status_display.py
│
├── submission_preprocessor.py     # Core support
├── report_generator.py
├── assignment_matcher.py
├── grading_validator.py
├── ai_grader.py
│
├── scripts/                       # Utility scripts
├── tests/                         # Test files
├── docs/                          # Documentation
├── data/                          # Data files
├── rubrics/                       # Rubrics
└── models/                        # Model code
```

**Total in root: ~25 essential files**

---

## 🚀 SAFE CLEANUP SCRIPT

I'll create an updated cleanup script that does Phase 1 safely.
