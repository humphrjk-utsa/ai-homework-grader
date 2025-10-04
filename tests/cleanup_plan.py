#!/usr/bin/env python3
"""
Plan for cleaning up extra files in homework_grader directory
"""

import os
from pathlib import Path

def analyze_files():
    """Analyze all files and categorize them"""
    
    # Essential core files (keep these)
    core_files = {
        # Main application
        'app.py': 'Main Streamlit application',
        'business_analytics_grader.py': 'Core AI grading system',
        'grading_validator.py': 'Grading validation',
        'report_generator.py': 'PDF report generation',
        
        # Interface modules
        'connect_web_interface.py': 'Web grading interface',
        'grading_interface.py': 'Results viewing interface',
        'training_interface.py': 'AI training interface',
        'assignment_manager.py': 'Assignment creation/upload',
        'assignment_editor.py': 'Assignment editing',
        
        # Supporting modules
        'model_status_display.py': 'Model status indicators',
        'unified_model_interface.py': 'Model interface abstraction',
        
        # Database and utilities
        'grading_database.db': 'Main database',
        'assignments/': 'Assignment files directory',
        'submissions/': 'Student submissions directory',
        'reports/': 'Generated reports directory',
    }
    
    # Test files (can be moved to tests/ subdirectory or removed)
    test_files = {
        'test_verbose_feedback.py': 'Verbose feedback testing',
        'test_pdf_verbose_feedback.py': 'PDF generation testing',
        'test_streamlit_feedback.py': 'Streamlit feedback testing',
        'test_training_interface.py': 'Training interface testing',
        'test_fixes.py': 'General fixes testing',
        'test_all_pages.py': 'All pages testing',
        'test_web_connection.py': 'Web connection testing',
        'test_ollama_grading.py': 'Ollama grading testing',
        'test_ollama_setup.py': 'Ollama setup testing',
        'test_pc_setup.py': 'PC setup testing',
        'test_which_grader.py': 'Grader selection testing',
    }
    
    # Debug/diagnostic files (can be removed or moved to debug/ subdirectory)
    debug_files = {
        'debug_grading_issue.py': 'Grading issue debugging',
        'diagnose_grading_issue.py': 'Issue diagnosis',
        'verify_verbose_feedback.py': 'Feedback verification',
        'verify_after_autofix.py': 'Post-fix verification',
        'fix_orphaned_submissions.py': 'Database fix utility',
        'fix_web_interface.py': 'Web interface fixes',
        'force_business_grader.py': 'Force grader selection',
    }
    
    # Demo/example files (can be removed)
    demo_files = {
        'demo_business_grading.py': 'Business grading demo',
        'demo_deon_review.py': 'Deon review demo',
        'generate_logan_text_report.py': 'Logan report generation',
        'corrected_logan_grader.py': 'Logan grader correction',
        'comprehensive_logan_grader.py': 'Comprehensive Logan grader',
        'detailed_comparison_report.py': 'Detailed comparison',
        'compare_students.py': 'Student comparison',
        'grade_logan_assignment.py': 'Logan assignment grading',
        'batch_grader.py': 'Batch grading utility',
    }
    
    # Setup/installation files (can be moved to setup/ subdirectory)
    setup_files = {
        'setup_assignment_1.py': 'Assignment 1 setup',
        'setup_mig.py': 'MIG setup',
        'optimize_ollama.py': 'Ollama optimization',
        'check_mig_support.py': 'MIG support check',
        'download_models_simple.py': 'Simple model download',
        'download_llama_cli.py': 'Llama CLI download',
        'download_qwen3_models.py': 'Qwen3 model download',
        'download_pc_models.py': 'PC model download',
        'quick_download_commands.py': 'Quick download commands',
        'pc_start.py': 'PC startup script',
        'pc_config.py': 'PC configuration',
    }
    
    # Model interface files (can be moved to models/ subdirectory)
    model_files = {
        'ollama_client.py': 'Ollama client interface',
        'ollama_two_model_grader.py': 'Ollama two-model grader',
        'mig_two_model_grader.py': 'MIG two-model grader',
        'mig_llamacpp_client.py': 'MIG LlamaCPP client',
        'mig_manager.py': 'MIG manager',
        'pc_llamacpp_client.py': 'PC LlamaCPP client',
        'pc_two_model_grader.py': 'PC two-model grader',
    }
    
    # Documentation files (keep but organize)
    doc_files = {
        'ALL_PAGES_FIXED_SUMMARY.md': 'Complete fix summary',
        'VERBOSE_FEEDBACK_SUMMARY.md': 'Verbose feedback summary',
        'TRAINING_INTERFACE_FIX.md': 'Training interface fix',
        'FIXES_SUMMARY.md': 'General fixes summary',
        'GRADING_SYSTEM_SUMMARY.md': 'Grading system summary',
        'TWO_MODEL_SYSTEM_GUIDE.md': 'Two-model system guide',
        'WEB_INTERFACE_GUIDE.md': 'Web interface guide',
        'HOW_TO_USE_TRAINING_INTERFACE.md': 'Training interface guide',
        'MIG_README.md': 'MIG setup readme',
        'PC_README.md': 'PC setup readme',
    }
    
    # Student files (keep)
    student_files = {
        'Balfour_Logan_homework_lesson_1.ipynb': 'Student notebook example',
    }
    
    return {
        'core': core_files,
        'test': test_files,
        'debug': debug_files,
        'demo': demo_files,
        'setup': setup_files,
        'model': model_files,
        'doc': doc_files,
        'student': student_files
    }

def create_cleanup_script():
    """Create a script to organize files"""
    
    categories = analyze_files()
    
    print("📁 File Organization Plan:")
    print("=" * 50)
    
    for category, files in categories.items():
        print(f"\n{category.upper()} FILES ({len(files)} files):")
        for filename, description in files.items():
            print(f"  📄 {filename} - {description}")
    
    print(f"\n📊 Summary:")
    total_files = sum(len(files) for files in categories.values())
    print(f"  Total files analyzed: {total_files}")
    print(f"  Core files (keep): {len(categories['core'])}")
    print(f"  Test files (organize): {len(categories['test'])}")
    print(f"  Debug files (can remove): {len(categories['debug'])}")
    print(f"  Demo files (can remove): {len(categories['demo'])}")
    print(f"  Setup files (organize): {len(categories['setup'])}")
    print(f"  Model files (organize): {len(categories['model'])}")
    print(f"  Doc files (organize): {len(categories['doc'])}")
    
    return categories

if __name__ == "__main__":
    create_cleanup_script()