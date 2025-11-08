#!/usr/bin/env python3
"""
Debug the full grading flow
"""

import json
from business_analytics_grader_v2 import BusinessAnalyticsGraderV2

# Initialize grader
rubric_path = "rubrics/assignment_7_rubric_v2.json"
solution_path = "data/raw/homework_lesson_7_string_datetime_SOLUTION_v2.ipynb"
notebook_path = "/Users/humphrjk/GitHub/ai-homework-grader-clean/data/raw/marccharlesanathaliaj_169558_11954692_Marc-Charles_Anathalia_homework_lesson_7_string_datetime.ipynb"

print("="*80)
print("TESTING FULL GRADING FLOW")
print("="*80)

grader = BusinessAnalyticsGraderV2(
    rubric_path=rubric_path,
    solution_path=solution_path
)

# Run validation only (not full grading)
print("\n🔍 Running 4-layer validation...")
validation_results = grader._run_4layer_validation(notebook_path)

print(f"\n📊 VALIDATION RESULTS:")
print(f"Base Score: {validation_results['base_score']:.1f}%")
print(f"Adjusted Score: {validation_results['adjusted_score']:.1f}%")
print(f"Penalty: {validation_results['total_penalty_percent']:.1f}%")

print(f"\n📈 SYSTEMATIC RESULTS:")
sys_result = validation_results['systematic_results']
print(f"Final Score: {sys_result['final_score']:.1f}/100")
print(f"Variables: {sys_result['variable_check']['found']}/{sys_result['variable_check']['total_required']}")

print(f"\n📋 SECTION BREAKDOWN:")
for section_id, section_data in sys_result['section_breakdown'].items():
    status_icon = "✅" if section_data['status'] == 'complete' else "❌"
    score = section_data.get('score', 0)
    points = section_data.get('points', 0)
    print(f"{status_icon} {section_data['name']}: {score:.1f}/{points} points")

print("\n" + "="*80)
