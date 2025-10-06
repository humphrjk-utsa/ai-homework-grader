#!/bin/bash

# Safe cleanup script for main directory
# Moves files to appropriate locations instead of deleting

echo "Safe Main Directory Cleanup"
echo "=============================="
echo ""

# Create archive directory if it doesn't exist
mkdir -p archive/old_summaries
mkdir -p archive/old_backups
mkdir -p submissions/assignment_3

# Count files to move
SUMMARY_COUNT=0
BACKUP_COUNT=0
SUBMISSION_COUNT=0

echo "Moving documentation summaries to archive/old_summaries/..."

# Move summary files
for file in AI_TRAINING_PAGE_ENHANCEMENTS.md BATCH_SUBMISSION_DEFAULT_SUMMARY.md CHANGES_SUMMARY.md CLEAN_PDF_REPORT_SUMMARY.md CLEAN_REPORT_IMPLEMENTATION_SUMMARY.md CRITICAL_GRADING_ISSUE.md DATABASE_FILTERING_IMPLEMENTATION_SUMMARY.md DONE_PREPROCESSING_COMPLETE.md DUAL_PANEL_INTERFACE_SUMMARY.md FEEDBACK_IMPROVEMENTS.md FINAL_SYSTEM_SUMMARY.md FIX_GIT_PATH.md FIX_LARGE_NOTEBOOK_HANG.md GPT_OSS_JSON_FIX_SUMMARY.md GRADING_FIXES_SUMMARY.md GRADING_IMPROVEMENTS.md MOVE_SETTINGS_PLAN.md NOTEBOOK_EXECUTION_FEATURE.md PERFORMANCE_DIAGNOSTICS_SUMMARY.md PREPROCESSING_IMPLEMENTATION_SUMMARY.md PREPROCESSING_QUICK_START.md PREPROCESSING_SYSTEM.md PREPROCESSING_VISUAL_SUMMARY.md PREPROCESSING_WITH_PENALTIES.md PROMPT_IMPROVEMENT_PLAN.md PROMPT_SYSTEM_SUMMARY.md QUICK_START_FEEDBACK_FIX.md README_FEEDBACK_CHANGES.md READY_TO_SWAP.md REPORT_FIXES_SUMMARY.md TEMPLATE_REMOVAL_SUMMARY.md TEST_FEEDBACK_QUALITY.md TIMEOUT_AND_AUTORESTART_FIX.md
do
    if [ -f "$file" ]; then
        mv "$file" archive/old_summaries/
        ((SUMMARY_COUNT++))
    fi
done

echo "Moved $SUMMARY_COUNT summary files"
echo ""

echo "Moving backup files to archive/old_backups/..."
for file in business_analytics_grader.py.bak grading_database.db.backup_20251003_105649 streamlit.log streamlit_output.log
do
    if [ -f "$file" ]; then
        mv "$file" archive/old_backups/
        ((BACKUP_COUNT++))
    fi
done

echo "Moved $BACKUP_COUNT backup files"
echo ""

echo "Moving student submissions to submissions/assignment_3/..."
for file in desantiagopalomaressalinasalejandro*.ipynb schoemandeon*.ipynb
do
    if [ -f "$file" ]; then
        mv "$file" submissions/assignment_3/
        ((SUBMISSION_COUNT++))
    fi
done

echo "Moved $SUBMISSION_COUNT student submission files"
echo ""

echo "=============================="
echo "CLEANUP COMPLETE!"
echo "=============================="
echo ""
echo "Summary:"
echo "  - Moved $SUMMARY_COUNT documentation summaries to archive/old_summaries/"
echo "  - Moved $BACKUP_COUNT backup files to archive/old_backups/"
echo "  - Moved $SUBMISSION_COUNT student submissions to submissions/assignment_3/"
echo ""
echo "All files preserved - nothing deleted!"
echo "Main directory is now cleaner and more organized."
echo ""
echo "To undo: Files are in archive/ and submissions/ directories"
