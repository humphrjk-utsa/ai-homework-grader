# AI Homework Grader - Repository Index

## Branch: DGX-TEST-For-Alex

Last Updated: January 22, 2026

---

## 📚 DGX & Disaggregated Inference Documentation

### Core DGX Documentation
1. **DGX_ORCHESTRATION_EXPLAINED.md** - How the DGX disaggregated system works
2. **DGX_CODE_BREAKDOWN.md** - Detailed code analysis of DGX orchestration
3. **DGX_QWEN_SETUP_PLAN.md** - Setup instructions for DGX Qwen model
4. **DISAGGREGATED_INFERENCE_SYSTEM_DOCUMENTATION.md** - Complete system documentation
5. **DISAGGREGATED_APP_GUIDE.md** - User guide for disaggregated inference
6. **DISAGGREGATED_STATUS.md** - Current status and configuration

### Performance & Analysis
7. **SPARK_CLUSTER_ANALYSIS.md** - Analysis of all-Spark cluster option (4 DGX Sparks)
8. **CURRENT_PARALLELISM_ANALYSIS.md** - Current bottlenecks and optimization opportunities
9. **ACTIVE_FILES_TEST_DGX.md** - Active files in Test-DGX branch

### Setup & Configuration
10. **SETUP_MAC2_FANS.md** - Mac Studio 2 fan control setup instructions

---

## 📖 Essential Documentation

### Architecture & Models
- **ARCHITECTURE_ANALYSIS.md** - System architecture overview
- **MODEL_SPECIFICATIONS.md** - Model specs (Qwen 3.0 Coder 30B, GPT-OSS 120B)

### Publication & Strategy
- **WHITE_PAPER_COMPLETE.md** - Complete white paper for publication
- **README_WHITE_PAPER.md** - White paper overview and target venues
- **PRODUCTIZATION_STRATEGY.md** - Commercialization strategy and market analysis

### Cleanup Documentation
- **CLEANUP_SUMMARY.md** - Summary of repository cleanup (90 files removed)
- **CLEANUP_PLAN.md** - Detailed cleanup plan

---

## 🐍 Active Python Files

### Main Application
- **app.py** - Main Streamlit application
- **system_health_check.py** - Auto-start health check system

### Grading System (Core)
- **business_analytics_grader_v2.py** - Main grading engine (ACTIVE VERSION)
- **disaggregated_client.py** - Client for DGX disaggregated inference
- **grading_validator.py** - Grading validation logic
- **report_generator.py** - PDF report generation
- **ai_grader.py** - AI grading utilities

### UI Components
- **connect_web_interface.py** - Grade submissions page
- **grading_interface.py** - View results page
- **enhanced_training_page.py** - Training interface
- **training_interface.py** - Training interface (legacy)
- **assignment_manager.py** - Assignment management
- **assignment_editor.py** - Assignment editing
- **prompt_manager.py** - Prompt management UI
- **model_status_display.py** - Model status display

### Supporting Modules
- **notebook_executor.py** - Execute Jupyter notebooks
- **notebook_validation.py** - Validate notebook structure
- **submission_preprocessor.py** - Preprocess submissions
- **output_comparator.py** - Compare outputs
- **score_validator.py** - Validate scores
- **anonymization_utils.py** - Anonymize student names
- **rubric_manager.py** - Manage rubrics
- **performance_logger.py** - Log performance metrics
- **correction_analyzer.py** - Analyze corrections
- **correction_helpers.py** - Correction utilities
- **assignment_matcher.py** - Match assignments
- **assignment_setup_helper.py** - Setup helper
- **migration_helper.py** - Database migration
- **model_config.py** - Model configuration
- **reflection_extractor.py** - Extract reflections
- **reflection_grader.py** - Grade reflections
- **output_verifier.py** - Verify outputs
- **submission_list_panel.py** - Submission list UI
- **tabbed_review_panel.py** - Tabbed review UI
- **enhanced_training_database.py** - Training database
- **enhanced_training_interface.py** - Enhanced training UI
- **modern_training_interface.py** - Modern training UI
- **unified_model_interface.py** - Unified model interface

---

## 📁 Key Directories

### Configuration & Inference
- **disaggregated_inference/** - DGX disaggregated inference configuration
  - `config_current.json` - Current network configuration
  - `prefill_server_vllm.py` - DGX prefill server
  - `decode_server_ollama.py` - Mac decode server

### Validators
- **validators/** - Validation modules
  - `rubric_driven_validator.py`
  - `smart_output_validator.py`

### Data & Storage
- **assignments/** - Assignment files
- **submissions/** - Student submissions
- **rubrics/** - Grading rubrics
- **reports/** - Generated reports
- **prompt_templates/** - Prompt templates
- **assignment_prompts/** - Assignment-specific prompts

### Databases
- **grading_database.db** - Main grading database
- **grading_system.db** - System database
- **homework_grader.db** - Homework grader database
- **enhanced_training.db** - Training database

---

## 🔧 Configuration Files

- **requirements.txt** - Python dependencies
- **server_config.json** - Server configuration
- **ollama_servers.json** - Ollama server configuration
- **LICENSE** - Project license
- **.gitignore** - Git ignore rules

---

## 🛠️ Utility Scripts

- **check_all_servers.sh** - Check all server health

---

## 🏗️ System Architecture

### Hardware Configuration
- **2 DGX Sparks** (169.254.150.105, 169.254.150.106) - Prefill servers
- **2 Mac Studios** (169.254.150.101, 169.254.150.102) - Decode servers
- **10Gb Ethernet Switch** - Network backbone
- **Thunderbolt Bridge** - Mac-to-Mac communication (10.55.0.x)

### Models
- **Qwen 3.0 Coder 30B** - Code analysis and grading
- **GPT-OSS 120B** - Feedback generation

### Performance
- **6-8x speedup** with current disaggregated setup
- **Potential 16x speedup** with all-Spark cluster (4 DGX Sparks)
- **Current bottleneck**: Serial submission processing (only 25% hardware utilization)

---

## 🚀 Quick Start

1. **Start the application:**
   ```bash
   cd ai-homework-grader
   source .venv/bin/activate
   streamlit run app.py
   ```

2. **Health check runs automatically** on startup:
   - Checks all 4 servers (2 DGX + 2 Mac)
   - Auto-starts Ollama if not running
   - Auto-starts decode servers if needed
   - Auto-starts Macs Fan Control on Mac Studio 1

3. **Access the UI:** http://localhost:8501

---

## 📊 Current Status

✅ **System Operational**
- All 4 servers healthy and loaded
- Auto-start health check integrated
- Network configuration complete
- DGX disaggregated inference working

✅ **Repository Clean**
- ~90 unused files removed
- All DGX documentation preserved
- Only active code remaining

✅ **Ready for Production**
- Comprehensive documentation
- White paper complete
- Productization strategy defined

---

## 🔄 Git Information

- **Current Branch:** DGX-TEST-For-Alex
- **Remote:** https://github.com/humphrjk-utsa/ai-homework-grader
- **Last Cleanup:** January 22, 2026
- **Files Removed:** ~90 (old code, tests, temp docs)
- **Files Kept:** All active code + DGX documentation

---

## 📝 Notes

- All removed files are preserved in git history
- Mac Studio 2 Macs Fan Control requires one-time manual setup (see SETUP_MAC2_FANS.md)
- System uses Test-DGX branch, not main branch
- Password for Mac Studios: Thorium2019!
