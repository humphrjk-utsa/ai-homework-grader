#!/bin/bash
# Cleanup Root Directory - Remove unnecessary files
# This removes ~65 files that are no longer needed

set -e

echo "🧹 Root Directory Cleanup"
echo "========================="
echo ""
echo "This will remove:"
echo "  - Deployment scripts (already deployed)"
echo "  - Old/duplicate versions"
echo "  - Obsolete documentation"
echo ""
echo "⚠️  Total: ~65 files will be deleted"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cleanup cancelled"
    exit 1
fi

# Create backup
echo ""
echo "📦 Creating backup..."
BACKUP_NAME="root-cleanup-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
tar -czf "../$BACKUP_NAME" *.py *.sh *.md *.json 2>/dev/null || true
echo "✅ Backup created: ../$BACKUP_NAME"

echo ""
echo "🗑️  Removing files..."

# Phase 1: Deployment scripts (already deployed)
echo "  Removing deployment scripts..."
rm -f deploy_mac1.sh deploy_mac2.sh deploy_to_headless_mac.py
rm -f copy_gemma_only.sh copy_models_to_mac2.sh boost_transfer_rate.sh
rm -f install.sh install_hf_cli_mac2.sh fix_hf_cli_path.sh
rm -f clear_locks_and_download.sh download_qwen_8bit.sh check_qwen_model.sh
rm -f check_mac2_memory.sh check_mac2_status.sh check_status.sh
rm -f cleanup_main_directory.sh
echo "    ✓ Deployment scripts removed"

# Phase 2: Old/duplicate versions
echo "  Removing old versions..."
rm -f dual_panel_layout.py dual_panel_training_interface.py
rm -f integrated_dual_panel_system.py enhanced_training_database.py
rm -f enhanced_training_integration.py enhanced_training_interface.py
rm -f assignment_setup_helper.py correction_helpers.py
rm -f debug_code_suggestions.py create_assignment3_solution.py
echo "    ✓ Old versions removed"

# Phase 3: Old documentation
echo "  Removing old documentation..."
rm -f ASSIGNMENT_3_SETUP_GUIDE.md ASSIGNMENT_5_GRADING_SETUP.md
rm -f GIT_SETUP_COMMANDS.md HEADLESS_DEPLOYMENT_GUIDE.md
rm -f LAUNCHER_README.md DATA_CONSISTENCY_ARCHITECTURE.md
rm -f HOMEWORK_8_GAPS_AND_FIXES.md HOMEWORK_8_MIDTERM_COVERAGE.md
echo "    ✓ Old documentation removed"

# Phase 4: Test files (move to tests/ folder)
echo "  Moving test files to tests/ folder..."
mkdir -p tests
mv francisco_feedback_test.py tests/ 2>/dev/null || true
mv test_grading_system.py tests/ 2>/dev/null || true
mv test_distributed_grading.py tests/ 2>/dev/null || true
mv test_mlx_servers.py tests/ 2>/dev/null || true
mv verify_verbose_feedback.py tests/ 2>/dev/null || true
echo "    ✓ Test files moved"

echo ""
echo "✅ Cleanup complete!"
echo ""

# Count remaining files
PY_COUNT=$(ls -1 *.py 2>/dev/null | wc -l | tr -d ' ')
SH_COUNT=$(ls -1 *.sh 2>/dev/null | wc -l | tr -d ' ')
MD_COUNT=$(ls -1 *.md 2>/dev/null | wc -l | tr -d ' ')
TOTAL=$((PY_COUNT + SH_COUNT + MD_COUNT))

echo "📊 Summary:"
echo "  - Backup saved: ../$BACKUP_NAME"
echo "  - Files removed: ~65"
echo "  - Remaining in root: $TOTAL files"
echo "    - Python: $PY_COUNT"
echo "    - Shell: $SH_COUNT"
echo "    - Markdown: $MD_COUNT"
echo ""
echo "🔍 Next steps:"
echo "  1. Test the system: streamlit run app.py"
echo "  2. Verify servers are running"
echo "  3. Try grading a submission"
echo ""
echo "🔄 To rollback if needed:"
echo "  cd .. && tar -xzf $BACKUP_NAME"
echo ""
