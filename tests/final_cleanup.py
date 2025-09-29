#!/usr/bin/env python3
"""
Final comprehensive cleanup of remaining files
"""

import os
import shutil
from pathlib import Path

def final_cleanup():
    """Move remaining non-essential files"""
    
    print("🧹 Final cleanup of remaining files...")
    
    # Additional files to move to appropriate directories
    
    # More test files
    additional_test_files = [
        'test_batch_processing.py',
        'test_bf16_models.py',
        'test_csv_export.py',
        'test_deon_submission.py',
        'test_drive_speed.py',
        'test_mlx_download.py',
        'test_model_loading.py',
        'test_single_qwen.py',
        'test_two_model_system.py',
        'test_two_model_timing.py',
        'mock_two_model_test.py',
        'simple_test.py',
        'quick_model_test.py'
    ]
    
    # More setup/download files
    additional_setup_files = [
        'download_gemma_qwen.py',
        'download_mlx_models.py',
        'download_with_progress.py',
        'fresh_mlx_download.py',
        'gemma_qwen_only.py',
        'essential_models.py',
        'monitor_downloads.py',
        'copy_models_guide.py',
        'enable_mig.bat',
        'enable_mig.ps1',
        'launch_setup.py',
        'setup_r_kernel.py',
        'start.py'
    ]
    
    # More model interface files
    additional_model_files = [
        'mlx_ai_client.py',
        'simple_mlx_client.py',
        'two_model_grader.py',
        'single_qwen_grader.py',
        'two_model_config.py'
    ]
    
    # Utility/helper files
    utility_files = [
        'ai_grader.py',
        'alternative_approaches.py',
        'assignment_matcher.py',
        'assignment_setup_helper.py',
        'check_available_models.py',
        'check_setup.py',
        'code_analyzer.py',
        'correction_helpers.py',
        'detailed_analyzer.py',
        'excel_summary.py',
        'feedback_generator.py',
        'fix_student_names.py',
        'language_detector.py',
        'migration_helper.py',
        'model_status.py',
        'pdf_report_generator.py',
        'regrade_logan_accurate.py',
        'rubric_manager.py',
        'two_model_report_generator.py'
    ]
    
    # Documentation files
    additional_doc_files = [
        'ASSIGNMENT_MANAGEMENT_README.md',
        'CONVERSATION_SUMMARY.md',
        'FIXED_WEB_INTERFACE.md',
        'QUICKSTART.md',
        'VERBOSE_FEEDBACK_TEST_INSTRUCTIONS.md'
    ]
    
    # Data/result files to archive
    data_files = [
        'deon_grading_results.json',
        'logan_comprehensive_results.json',
        'logan_corrected_results.json',
        'logan_grading_results.json',
        'ollama_config.json',
        'assignment_1_rubric.json',
        'assignment_2_rubric.json'
    ]
    
    # PDF reports to move to reports/
    pdf_files = [
        '_YOUR_NAME_HERE_report_20250922_140413[2].pdf',
        'Logan_Balfour_report_20250922_141308.pdf'
    ]
    
    # Notebook files to move to assignments/ or submissions/
    notebook_files = [
        'homework_lesson_2_data_cleaning (2).ipynb',
        'homework_lesson_2_solution_corrected.ipynb',
        'homework_lesson_2_solution.ipynb'
    ]
    
    moved_count = 0
    
    # Move additional test files
    for filename in additional_test_files:
        if os.path.exists(filename):
            shutil.move(filename, f'tests/{filename}')
            print(f"📄 Moved {filename} → tests/")
            moved_count += 1
    
    # Move additional setup files
    for filename in additional_setup_files:
        if os.path.exists(filename):
            shutil.move(filename, f'setup/{filename}')
            print(f"📄 Moved {filename} → setup/")
            moved_count += 1
    
    # Move additional model files
    for filename in additional_model_files:
        if os.path.exists(filename):
            shutil.move(filename, f'models/{filename}')
            print(f"📄 Moved {filename} → models/")
            moved_count += 1
    
    # Move utility files to archive (they're helper modules we don't need in root)
    for filename in utility_files:
        if os.path.exists(filename):
            shutil.move(filename, f'archive/{filename}')
            print(f"📄 Archived {filename} → archive/")
            moved_count += 1
    
    # Move additional documentation
    for filename in additional_doc_files:
        if os.path.exists(filename):
            shutil.move(filename, f'docs/{filename}')
            print(f"📄 Moved {filename} → docs/")
            moved_count += 1
    
    # Move data files to archive
    for filename in data_files:
        if os.path.exists(filename):
            shutil.move(filename, f'archive/{filename}')
            print(f"📄 Archived {filename} → archive/")
            moved_count += 1
    
    # Move PDF files to reports
    for filename in pdf_files:
        if os.path.exists(filename):
            shutil.move(filename, f'reports/{filename}')
            print(f"📄 Moved {filename} → reports/")
            moved_count += 1
    
    # Move notebook files to assignments
    for filename in notebook_files:
        if os.path.exists(filename):
            shutil.move(filename, f'assignments/{filename}')
            print(f"📄 Moved {filename} → assignments/")
            moved_count += 1
    
    print(f"\n✅ Final cleanup complete! Moved {moved_count} additional files.")
    
    # Show final core files
    print(f"\n📋 Final core files in root directory:")
    
    remaining_files = []
    for item in os.listdir('.'):
        if os.path.isfile(item) and not item.startswith('.'):
            remaining_files.append(item)
    
    # Expected core files
    expected_core = [
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
        'unified_model_interface.py',
        'README.md',
        'requirements.txt',
        'grading_database.db'
    ]
    
    for filename in sorted(remaining_files):
        if filename in expected_core:
            print(f"   ✅ {filename} (core)")
        else:
            print(f"   ⚠️ {filename} (unexpected)")
    
    print(f"\n📊 Summary:")
    print(f"   Total files in root: {len(remaining_files)}")
    print(f"   Expected core files: {len(expected_core)}")
    
    # Show directory sizes
    subdirs = ['tests', 'docs', 'models', 'setup', 'archive', 'assignments', 'submissions', 'reports']
    print(f"\n📁 Subdirectory contents:")
    for subdir in subdirs:
        if os.path.exists(subdir):
            file_count = len([f for f in os.listdir(subdir) if os.path.isfile(os.path.join(subdir, f))])
            print(f"   📂 {subdir}/: {file_count} files")

if __name__ == "__main__":
    final_cleanup()