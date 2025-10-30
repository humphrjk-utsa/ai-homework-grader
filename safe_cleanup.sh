#!/bin/bash
# Safe Cleanup Script - Removes only obviously unused files
# Review this script before running!

set -e  # Exit on error

echo "🧹 AI Homework Grader - Safe Cleanup"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Run this from the project root."
    exit 1
fi

echo "📋 This script will remove:"
echo "  - Test files (5 files)"
echo "  - Old versions (3 files)"
echo "  - Archive folder"
echo "  - Old documentation (2 files)"
echo ""
echo "✅ Will KEEP all monitor files (useful for debugging)"
echo ""
echo "⚠️  IMPORTANT: A backup will be created first"
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
BACKUP_NAME="ai-homework-grader-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
cd ..
tar -czf "$BACKUP_NAME" ai-homework-grader-clean/
echo "✅ Backup created: $BACKUP_NAME"
cd ai-homework-grader-clean

echo ""
echo "🗑️  Removing files..."

# Remove test files
echo "  Removing test files..."
rm -f francisco_feedback_test.py 2>/dev/null && echo "    ✓ francisco_feedback_test.py" || echo "    - francisco_feedback_test.py (not found)"
rm -f test_grading_system.py 2>/dev/null && echo "    ✓ test_grading_system.py" || echo "    - test_grading_system.py (not found)"
rm -f test_distributed_grading.py 2>/dev/null && echo "    ✓ test_distributed_grading.py" || echo "    - test_distributed_grading.py (not found)"
rm -f test_mlx_servers.py 2>/dev/null && echo "    ✓ test_mlx_servers.py" || echo "    - test_mlx_servers.py (not found)"
rm -f verify_verbose_feedback.py 2>/dev/null && echo "    ✓ verify_verbose_feedback.py" || echo "    - verify_verbose_feedback.py (not found)"

# Remove old versions
echo "  Removing old versions..."
rm -f training_interface_reference.py 2>/dev/null && echo "    ✓ training_interface_reference.py" || echo "    - training_interface_reference.py (not found)"
rm -f alternative_approaches.py 2>/dev/null && echo "    ✓ alternative_approaches.py" || echo "    - alternative_approaches.py (not found)"
rm -f standalone_gemma_server.py 2>/dev/null && echo "    ✓ standalone_gemma_server.py" || echo "    - standalone_gemma_server.py (not found)"

# Remove archive folder
echo "  Removing archive folder..."
if [ -d "archive" ]; then
    rm -rf archive/
    echo "    ✓ archive/ folder removed"
else
    echo "    - archive/ folder (not found)"
fi

# Keep all monitor files - they're useful for debugging
echo "  Keeping all monitor files (useful for debugging)"

# Remove old docs
echo "  Removing old documentation..."
rm -f CLEANUP_SUMMARY.md 2>/dev/null && echo "    ✓ CLEANUP_SUMMARY.md" || echo "    - CLEANUP_SUMMARY.md (not found)"
rm -f SYSTEM_ARCHITECTURE_DOCUMENTATION.md 2>/dev/null && echo "    ✓ SYSTEM_ARCHITECTURE_DOCUMENTATION.md" || echo "    - SYSTEM_ARCHITECTURE_DOCUMENTATION.md (not found)"

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📊 Summary:"
echo "  - Backup saved: ../$BACKUP_NAME"
echo "  - Files removed: ~10 files + archive folder"
echo "  - Monitor files: KEPT (useful for debugging)"
echo "  - Space saved: ~5-10 MB"
echo ""
echo "🔍 Next steps:"
echo "  1. Test the system: streamlit run app.py"
echo "  2. Verify servers: curl http://localhost:5001/health"
echo "  3. Try grading a test submission"
echo ""
echo "🔄 To rollback if needed:"
echo "  cd .. && tar -xzf $BACKUP_NAME"
echo ""
