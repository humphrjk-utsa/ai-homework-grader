# Root Directory Cleanup - November 1, 2024

## Summary
Cleaned up root directory by archiving non-essential files while preserving all active system components.

## Files Moved to Archive

### Documentation (docs/)
- 50+ markdown documentation files
- Instruction files (ASSIGNMENT_2V1_PROMPT_INSTRUCTIONS.txt, etc.)
- Comparison reports and templates
- Kept: README.md, QUICK_REFERENCE.md

### Test Files (tests/)
- test_*.py files (8 files)
- test_*.json files
- All test-related files moved to tests/ subdirectory

### Scripts (scripts/)
- restart_*.sh files (multiple restart scripts)
- start_*.sh files (server startup scripts)
- switch_*.sh files (model switching scripts)
- verify_*.sh files (verification scripts)
- Utility Python scripts (analyze_performance_logs.py, etc.)
- Kept: clean_restart.sh, monitor_macs.sh, quick_restart.sh, safe_cleanup.sh

### Backups (backups/)
- *.backup files
- *.log files
- .DS_Store

### Duplicate/Old Files Removed
- gpt_oss_server_working.py (root) - duplicate of servers/gpt_oss_server_working.py
- qwen_8bit_server.py - old version
- Various utility scripts no longer in active use

## Files Kept in Root (Active System)

### Core Application
- app.py - Main Streamlit application
- business_analytics_grader.py - Primary grader
- business_analytics_grader_v2.py - Enhanced V2 grader
- connect_web_interface.py - Grading interface
- enhanced_training_page.py - Training interface
- training_interface.py - Training system
- grading_interface.py - Results viewing

### Managers & Helpers
- assignment_manager.py
- assignment_editor.py
- assignment_matcher.py
- assignment_setup_helper.py
- prompt_manager.py
- server_manager.py
- rubric_manager.py
- model_config.py
- model_status_display.py

### Utilities
- anonymization_utils.py
- correction_helpers.py
- correction_analyzer.py
- notebook_executor.py
- notebook_validation.py
- output_comparator.py
- output_verifier.py
- performance_logger.py
- score_validator.py
- submission_preprocessor.py

### Database & Interfaces
- enhanced_training_database.py
- enhanced_training_interface.py
- modern_training_interface.py
- grading_validator.py
- unified_model_interface.py

### Monitoring
- monitor_app.py
- monitor_dashboard.py
- monitor_dashboard_full.py
- monitor_macs.sh

### Configuration
- distributed_config.json - Distributed MLX system config
- server_config.json - Server definitions
- requirements.txt

### Databases
- grading_database.db
- enhanced_training.db

### Essential Scripts
- clean_restart.sh
- quick_restart.sh
- safe_cleanup.sh
- cleanup_root_directory.sh

## Directories Preserved
All directories remain intact:
- servers/ - Active MLX servers
- models/ - Model clients and utilities
- validators/ - Validation systems
- prompt_templates/ - Prompt templates
- rubrics/ - Assignment rubrics
- submissions/ - Student submissions
- assignments/ - Assignment templates
- data/ - Raw data and solutions
- reports/ - Generated reports
- grading_results_*/ - Grading results
- And all other directories

## Restoration
If any archived file is needed, it can be found in:
`archive/cleanup_nov1_2024/`

Subdirectories:
- docs/ - Documentation and markdown files
- tests/ - Test files
- scripts/ - Shell scripts and utilities
- backups/ - Backup files and logs
