# Safe Cleanup Plan - Files to Remove

## 🔍 Analysis Method

1. Check what `app.py` imports (core system)
2. Check what those imports depend on
3. Identify test files, duplicates, and old versions
4. Mark safe-to-delete files

---

## ✅ CORE OPERATIONAL FILES (DO NOT DELETE)

### Main Application
- `app.py` - Main Streamlit application
- `business_analytics_grader.py` - Core grading engine

### Web Interface Components
- `assignment_manager.py` - Assignment creation/upload
- `assignment_editor.py` - Assignment editing
- `training_interface.py` - AI training interface
- `enhanced_training_page.py` - Enhanced training UI
- `connect_web_interface.py` - Grading page
- `grading_interface.py` - Results viewing
- `prompt_manager.py` - Prompt management
- `model_status_display.py` - Server status display

### Core Grading Components
- `submission_preprocessor.py` - Cleans submissions
- `report_generator.py` - Generates PDF reports
- `assignment_matcher.py` - Matches assignments to rubrics

### Model/Server Components
- `models/distributed_mlx_client.py` - Distributed grading client
- `gpt_oss_server_working.py` - GPT-OSS server (Mac 1)
- `qwen_8bit_server.py` - Qwen server (Mac 2)
- `server_manager.py` - Server management

### Configuration
- `distributed_config.json` - Server configuration
- `server_config.json` - Server settings

### Data/Rubrics
- `rubrics/*.json` - All rubric files
- `data/` - All data files
- `sample_datasets/` - Sample data for assignments

---

## 🗑️ SAFE TO DELETE

### Category 1: Test/Debug Files
```
francisco_feedback_test.py
test_grading_system.py
test_distributed_grading.py
test_mlx_servers.py
verify_verbose_feedback.py
debug_grading_issue.py
```

### Category 2: Old/Duplicate Versions
```
training_interface_reference.py  (old version)
grading_interface_old.py  (if exists)
connect_web_interface_old.py  (if exists)
```

### Category 3: One-time Setup Scripts
```
setup_distributed_system.py  (already configured)
deploy_to_headless_mac.py  (deployment done)
migration_helper.py  (migrations complete)
migrations/  (entire folder if migrations done)
```

### Category 4: Alternative Approaches (Not Used)
```
alternative_approaches.py
standalone_gemma_server.py  (using gpt_oss_server_working.py)
```

### Category 5: Monitoring/Analysis (Optional - Keep if Useful)
```
analyze_performance_logs.py  (useful for debugging)
monitor_dashboard.py  (useful for monitoring)
monitor_dashboard_full.py  (duplicate of above)
monitor_app.py  (another duplicate)
performance_logger.py  (useful for tracking)
```

### Category 6: Archive Folder
```
archive/  (entire folder - already archived)
```

### Category 7: Documentation Duplicates
```
CLEANUP_SUMMARY.md  (old cleanup doc)
SYSTEM_ARCHITECTURE_DOCUMENTATION.md  (duplicate of SYSTEM_ARCHITECTURE.md)
```

---

## 📋 SAFE CLEANUP COMMANDS

### Step 1: Create Backup (IMPORTANT!)
```bash
# Create backup of entire project
cd ..
tar -czf ai-homework-grader-backup-$(date +%Y%m%d).tar.gz ai-homework-grader-clean/
cd ai-homework-grader-clean
```

### Step 2: Remove Test Files
```bash
rm -f francisco_feedback_test.py
rm -f test_grading_system.py
rm -f test_distributed_grading.py
rm -f test_mlx_servers.py
```

### Step 3: Remove Old Versions
```bash
rm -f training_interface_reference.py
rm -f alternative_approaches.py
rm -f standalone_gemma_server.py
```

### Step 4: Remove Setup Scripts (Already Done)
```bash
rm -f setup_distributed_system.py
rm -f deploy_to_headless_mac.py
rm -f migration_helper.py
rm -rf migrations/
```

### Step 5: Remove Archive (Already Archived)
```bash
rm -rf archive/
```

### Step 6: Remove Duplicate Docs
```bash
rm -f CLEANUP_SUMMARY.md
rm -f SYSTEM_ARCHITECTURE_DOCUMENTATION.md
```

### Step 7: Remove Duplicate Monitors (Keep One)
```bash
# Keep monitor_dashboard.py, remove others
rm -f monitor_dashboard_full.py
rm -f monitor_app.py
```

---

## ⚠️ MAYBE DELETE (Review First)

### Monitoring Tools (Useful for Debugging)
- `analyze_performance_logs.py` - Analyzes performance
- `monitor_dashboard.py` - Real-time monitoring
- `performance_logger.py` - Logs performance metrics

**Recommendation:** Keep these for now, useful for troubleshooting

### Helper Scripts
- `anonymization_utils.py` - Anonymizes student data
- `notebook_validation.py` - Validates notebooks
- `notebook_executor.py` - Executes notebooks
- `output_verifier.py` - Verifies outputs
- `correction_helpers.py` - Helps with corrections

**Recommendation:** Keep these, they support core functionality

### Deployment Scripts
- `restart_servers.sh` - Restarts servers
- `swap_models.sh` - Swaps models
- `RESTART_NOW.sh` - Emergency restart
- `monitor_macs.sh` - Monitors both Macs

**Recommendation:** Keep these, useful for maintenance

---

## 🎯 CONSERVATIVE CLEANUP (Recommended)

**Remove only obviously safe files:**

```bash
# Create backup first!
cd ..
tar -czf ai-homework-grader-backup-$(date +%Y%m%d).tar.gz ai-homework-grader-clean/
cd ai-homework-grader-clean

# Remove test files
rm -f francisco_feedback_test.py
rm -f test_grading_system.py
rm -f test_distributed_grading.py
rm -f test_mlx_servers.py
rm -f verify_verbose_feedback.py

# Remove old versions
rm -f training_interface_reference.py
rm -f alternative_approaches.py
rm -f standalone_gemma_server.py

# Remove archive folder
rm -rf archive/

# Remove duplicate monitors
rm -f monitor_dashboard_full.py
rm -f monitor_app.py

# Remove old cleanup docs
rm -f CLEANUP_SUMMARY.md
```

**Expected space saved:** ~5-10 MB
**Risk level:** Very low
**Impact on system:** None

---

## 📊 Estimated Cleanup Results

### Before:
- Python files: ~60
- Total size: ~50 MB
- Archive folder: ~10 MB

### After Conservative Cleanup:
- Python files: ~50
- Total size: ~40 MB
- Cleaner structure

### After Aggressive Cleanup:
- Python files: ~35
- Total size: ~30 MB
- Minimal structure

**Recommendation:** Start with conservative cleanup, test system, then do more if needed.

---

## ✅ Verification After Cleanup

```bash
# Test the system still works
streamlit run app.py

# Check servers are running
curl http://localhost:5001/health
curl http://10.55.0.2:5002/health

# Try grading a test submission
# Upload a notebook and verify it grades successfully
```

---

## 🔄 Rollback Plan

If something breaks:

```bash
# Stop everything
pkill -f streamlit
pkill -f gpt_oss_server
ssh jamiehumphries@10.55.0.2 "pkill -f qwen"

# Restore from backup
cd ..
rm -rf ai-homework-grader-clean/
tar -xzf ai-homework-grader-backup-YYYYMMDD.tar.gz

# Restart
cd ai-homework-grader-clean
python gpt_oss_server_working.py &
ssh jamiehumphries@10.55.0.2 "cd ~ && python qwen_8bit_server.py &"
streamlit run app.py
```

---

## 📝 Summary

**Safe to delete immediately:**
- Test files (5 files)
- Old versions (3 files)
- Archive folder (entire folder)
- Duplicate monitors (2 files)
- Old docs (2 files)

**Total:** ~12 files + archive folder
**Risk:** Very low
**Benefit:** Cleaner codebase, easier to navigate

**DO NOT DELETE:**
- Anything imported by app.py
- Server files (gpt_oss, qwen)
- Configuration files
- Rubrics and data
- Active monitoring tools
