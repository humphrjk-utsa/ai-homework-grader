# Cleanup Plan for ai-homework-grader

## Files to KEEP

### Active Python Files (Used by app.py)
- app.py (main application)
- assignment_manager.py
- assignment_editor.py
- training_interface.py
- enhanced_training_page.py
- connect_web_interface.py
- grading_interface.py
- prompt_manager.py
- model_status_display.py
- system_health_check.py

### Core Grading System (Used by connect_web_interface)
- business_analytics_grader_v2.py (ACTIVE VERSION)
- grading_validator.py
- report_generator.py
- ai_grader.py
- anonymization_utils.py
- notebook_executor.py
- submission_preprocessor.py

### Disaggregated Inference System (Used by grader_v2)
- disaggregated_client.py
- prompt_manager.py (already listed)
- notebook_validation.py
- score_validator.py
- output_comparator.py

### Validators (Used by grader_v2)
- validators/ (entire directory)

### Supporting Files
- model_config.py
- performance_logger.py
- correction_analyzer.py
- correction_helpers.py
- rubric_manager.py
- server_manager.py
- unified_model_interface.py
- reflection_extractor.py
- reflection_grader.py
- output_verifier.py
- assignment_matcher.py
- assignment_setup_helper.py
- migration_helper.py
- submission_list_panel.py
- tabbed_review_panel.py
- enhanced_training_database.py
- enhanced_training_interface.py
- modern_training_interface.py

### Configuration Files
- requirements.txt
- server_config.json
- ollama_servers.json
- disaggregated_inference/ (entire directory)

### DGX-Specific Documentation (KEEP ALL)
- DGX_CODE_BREAKDOWN.md
- DGX_ORCHESTRATION_EXPLAINED.md
- DGX_QWEN_SETUP_PLAN.md
- DISAGGREGATED_APP_GUIDE.md
- DISAGGREGATED_INFERENCE_SYSTEM_DOCUMENTATION.md
- DISAGGREGATED_STATUS.md
- SPARK_CLUSTER_ANALYSIS.md
- CURRENT_PARALLELISM_ANALYSIS.md
- ACTIVE_FILES_TEST_DGX.md
- SETUP_MAC2_FANS.md

### Essential Documentation
- README_WHITE_PAPER.md
- WHITE_PAPER_COMPLETE.md
- MODEL_SPECIFICATIONS.md
- PRODUCTIZATION_STRATEGY.md
- ARCHITECTURE_ANALYSIS.md
- LICENSE

### Utility Scripts
- check_all_servers.sh
- system_health_check.py (already listed)

## Files to REMOVE

### Old/Broken Versions
- business_analytics_grader_old.py
- business_analytics_grader_original.py
- business_analytics_grader_v2_broken.py
- business_analytics_grader_v2_master.py
- business_analytics_grader.py (old version, v2 is active)

### Test Files
- test_batch_grading.py
- test_dgx_connection.py
- test_dgx_grading.py
- test_disaggregated_client.py
- test_disaggregated_setup.py
- test_grade_marc.py
- test_grader_disaggregated.py
- test_grading_result.json
- test_metrics_display.py
- test_output_comparison.py
- test_penalty_logic.py
- test_reflection_part6.json

### Temporary/Unused Scripts
- fix_network_config.sh (network already configured)
- clean_restart.sh
- cleanup_root_directory.sh
- create_production_version.sh
- quick_restart.sh
- restart_oss_server.sh
- safe_cleanup.sh
- setup_mac2_autostart.sh
- setup_macs_fan_autostart.sh
- monitor_macs.sh

### Unused Python Files
- alternative_approaches.py
- create_solution_notebook.py
- create_solution.py
- eds_to_json_exporter_fixed.py
- grade_with_systematic_validator.py
- monitor_app.py
- monitor_dashboard_full.py
- monitor_dashboard.py
- pcr_curve_viewer.py
- regrade_with_new_validator.py
- solution_v2_simple.R

### Non-DGX Documentation (Remove)
- ACTION_PLAN_FINAL.md
- AI_GRADING_CONTEXT.md
- assignment_7_fix_plan.md
- assignment_7_scoring_analysis.md
- CRITICAL_FINDING.md
- FEEDBACK_ACCURACY_ANALYSIS.md
- FILE_UPLOAD_FIXES.md
- FINAL_DELIVERABLES.md
- FINAL_READY_FOR_PRODUCTION.md
- FINAL_SOLUTION_EXPLANATION.md
- FINAL_STATUS.md
- FLEXIBLE_PARTIAL_CREDIT_SUMMARY.md
- GRADER_V2_READY.md
- GRADING_ISSUE_ANALYSIS.md
- GRADING_ISSUES_FOUND.md
- GRADING_PHASES.md
- GRADING_SYSTEM_AUDIT.md
- kathryn_emerick_analysis.md
- MAC2_MANUAL_SETUP.md (superseded by SETUP_MAC2_FANS.md)
- MASTER_BRANCH_ISSUES.md
- MIDTERM_SETUP_COMPLETE.md
- MODELS_AND_USAGE_SUMMARY.md
- NOTEBOOK_SOLUTION_COMPLETE.md
- OLLAMA_PROMPTS_SUCCESS.md
- OPTION_A_IMPLEMENTATION.md
- OUTPUT_COMPARISON_FLOW.md
- PCR_VIEWER_GUIDE.md
- PHASE_1_2_FIXES.md
- PRODUCTION_SYSTEM_AUDIT.md
- PRODUCTIZATION_STEPS.md
- PUBLICATION_SUMMARY.md
- REFLECTION_GRADING_FLOW.md
- REFLECTION_SECTION_DETECTION.md
- REPORT_FORMATTING_IMPROVEMENTS.md
- SCORING_ISSUE_RESOLUTION.md
- SOLUTION_AND_RUBRIC_CREATED.md
- SOLUTION_COMPLETE_FINAL.md
- SOLUTION_SUMMARY.md
- SUCCESS.md
- SYSTEM_DIAGRAMS.md
- SYSTEM_OVERVIEW.txt
- VALIDATOR_ISSUE_ANALYSIS.md
- VISUAL_SUMMARY.md
- WHITE_PAPER_PART1.md through WHITE_PAPER_PART8.md (consolidated into WHITE_PAPER_COMPLETE.md)
- WHITE_PAPER.md (old version)

### Unused Config Files
- distributed_config.json.mlx_not_used

### Temporary Data Files
- homework_lesson_7_SOLUTION_v2.md
- Homework_report (6).pdf

### Database Files (Keep for now - contain data)
- grading_database.db
- grading_system.db
- homework_grader.db
- enhanced_training.db
