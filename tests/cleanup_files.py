#!/usr/bin/env python3
"""
Clean up and organize files in homework_grader directory
"""

import os
import shutil
from pathlib import Path

def cleanup_files():
    """Organize files into proper directories"""
    
    print("🧹 Cleaning up homework_grader directory...")
    
    # Create subdirectories
    subdirs = ['tests', 'docs', 'models', 'setup', 'archive']
    for subdir in subdirs:
        os.makedirs(subdir, exist_ok=True)
        print(f"📁 Created directory: {subdir}/")
    
    # Files to move to tests/
    test_files = [
        'test_verbose_feedback.py',
        'test_pdf_verbose_feedback.py', 
        'test_streamlit_feedback.py',
        'test_training_interface.py',
        'test_fixes.py',
        'test_all_pages.py',
        'test_web_connection.py',
        'test_ollama_grading.py',
        'test_ollama_setup.py',
        'test_pc_setup.py',
        'test_which_grader.py',
        'cleanup_plan.py'  # This file too
    ]
    
    # Files to move to docs/
    doc_files = [
        'ALL_PAGES_FIXED_SUMMARY.md',
        'VERBOSE_FEEDBACK_SUMMARY.md',
        'TRAINING_INTERFACE_FIX.md',
        'FIXES_SUMMARY.md',
        'GRADING_SYSTEM_SUMMARY.md',
        'TWO_MODEL_SYSTEM_GUIDE.md',
        'WEB_INTERFACE_GUIDE.md',
        'HOW_TO_USE_TRAINING_INTERFACE.md',
        'MIG_README.md',
        'PC_README.md'
    ]
    
    # Files to move to models/
    model_files = [
        'ollama_client.py',
        'ollama_two_model_grader.py',
        'mig_two_model_grader.py',
        'mig_llamacpp_client.py',
        'mig_manager.py',
        'pc_llamacpp_client.py',
        'pc_two_model_grader.py'
    ]
    
    # Files to move to setup/
    setup_files = [
        'setup_assignment_1.py',
        'setup_mig.py',
        'optimize_ollama.py',
        'check_mig_support.py',
        'download_models_simple.py',
        'download_llama_cli.py',
        'download_qwen3_models.py',
        'download_pc_models.py',
        'quick_download_commands.py',
        'pc_start.py',
        'pc_config.py'
    ]
    
    # Files to archive (debug/demo files we don't need anymore)
    archive_files = [
        'debug_grading_issue.py',
        'diagnose_grading_issue.py',
        'verify_verbose_feedback.py',
        'verify_after_autofix.py',
        'fix_orphaned_submissions.py',
        'fix_web_interface.py',
        'force_business_grader.py',
        'demo_business_grading.py',
        'demo_deon_review.py',
        'generate_logan_text_report.py',
        'corrected_logan_grader.py',
        'comprehensive_logan_grader.py',
        'detailed_comparison_report.py',
        'compare_students.py',
        'grade_logan_assignment.py',
        'batch_grader.py'
    ]
    
    # Move files
    moved_count = 0
    
    # Move test files
    for filename in test_files:
        if os.path.exists(filename):
            shutil.move(filename, f'tests/{filename}')
            print(f"📄 Moved {filename} → tests/")
            moved_count += 1
    
    # Move documentation files
    for filename in doc_files:
        if os.path.exists(filename):
            shutil.move(filename, f'docs/{filename}')
            print(f"📄 Moved {filename} → docs/")
            moved_count += 1
    
    # Move model files
    for filename in model_files:
        if os.path.exists(filename):
            shutil.move(filename, f'models/{filename}')
            print(f"📄 Moved {filename} → models/")
            moved_count += 1
    
    # Move setup files
    for filename in setup_files:
        if os.path.exists(filename):
            shutil.move(filename, f'setup/{filename}')
            print(f"📄 Moved {filename} → setup/")
            moved_count += 1
    
    # Archive old files
    for filename in archive_files:
        if os.path.exists(filename):
            shutil.move(filename, f'archive/{filename}')
            print(f"📄 Archived {filename} → archive/")
            moved_count += 1
    
    print(f"\n✅ Cleanup complete! Moved {moved_count} files.")
    
    # Show remaining core files
    print(f"\n📋 Remaining core files:")
    core_files = [
        'app.py',
        'business_analytics_grader.py',
        'grading_validator.py',
        'report_generator.py',
        'connect_web_interface.py',
        'grading_interface.py',
        'training_interface.py',
        'assignment_manager.py',
        'assignment_editor.py',
        'model_status_display.py',
        'unified_model_interface.py'
    ]
    
    for filename in core_files:
        if os.path.exists(filename):
            print(f"   ✅ {filename}")
        else:
            print(f"   ❌ {filename} (missing)")
    
    # Show directories
    print(f"\n📁 Directory structure:")
    print(f"   📂 homework_grader/")
    print(f"   ├── 📄 app.py (main application)")
    print(f"   ├── 📄 *.py (core modules)")
    print(f"   ├── 📂 tests/ ({len(test_files)} test files)")
    print(f"   ├── 📂 docs/ ({len(doc_files)} documentation files)")
    print(f"   ├── 📂 models/ ({len(model_files)} model interface files)")
    print(f"   ├── 📂 setup/ ({len(setup_files)} setup/installation files)")
    print(f"   ├── 📂 archive/ ({len(archive_files)} archived files)")
    print(f"   ├── 📂 assignments/ (assignment files)")
    print(f"   ├── 📂 submissions/ (student submissions)")
    print(f"   └── 📂 reports/ (generated reports)")

def create_readme():
    """Create a README for the organized structure"""
    
    readme_content = """# Homework Grader - Clean Structure

## 🚀 Quick Start
```bash
streamlit run app.py
```

## 📁 Directory Structure

### Core Files (Root Directory)
- `app.py` - Main Streamlit application
- `business_analytics_grader.py` - AI grading system (Qwen 3.0 + Gemma 3.0)
- `grading_validator.py` - Grading validation and consistency checks
- `report_generator.py` - PDF report generation with code examples
- `connect_web_interface.py` - Web grading interface
- `grading_interface.py` - Results viewing and management
- `training_interface.py` - AI training and correction interface
- `assignment_manager.py` - Assignment creation and upload
- `assignment_editor.py` - Assignment editing and management
- `model_status_display.py` - Model status indicators
- `unified_model_interface.py` - Model interface abstraction

### Subdirectories

#### `tests/` - Test Files
- Various test scripts for validating functionality
- Run tests to verify system components

#### `docs/` - Documentation
- Setup guides and system documentation
- Feature summaries and fix documentation

#### `models/` - Model Interface Files
- Client interfaces for different AI model systems
- Ollama, MIG, and PC-specific implementations

#### `setup/` - Installation & Setup
- Model download scripts
- System configuration files
- Setup utilities for different environments

#### `archive/` - Archived Files
- Old debug and demo files
- Kept for reference but not needed for operation

#### `assignments/` - Assignment Files
- Template and solution notebooks
- Assignment configuration files

#### `submissions/` - Student Work
- Uploaded student notebooks
- Organized by assignment

#### `reports/` - Generated Reports
- PDF reports with comprehensive feedback
- Organized by assignment and student

## 🎯 Key Features
- **Comprehensive AI Grading** with Business Analytics focus
- **Verbose Feedback** with 6 detailed sections
- **PDF Reports** with R code examples
- **AI Training Interface** for improving accuracy
- **Two-Model System** for parallel processing
- **Professional Reports** suitable for academic use

## 📊 System Status
- ✅ All pages working correctly
- ✅ Comprehensive feedback implemented
- ✅ PDF reports with code examples
- ✅ AI training interface functional
- ✅ Database relationships fixed
- ✅ Clean, organized codebase
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    
    print("📄 Created README.md with clean structure documentation")

if __name__ == "__main__":
    cleanup_files()
    create_readme()
    print("\n🎉 Cleanup complete! The homework_grader directory is now organized and clean.")