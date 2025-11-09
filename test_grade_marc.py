#!/usr/bin/env python3
"""
Test grading Marc-Charles submission with a7v3
"""

import sqlite3
from business_analytics_grader_v2 import BusinessAnalyticsGraderV2

# Use assignment 6 directly
rubric_path = "rubrics/assignment_6_rubric.json"
solution_path = "data/raw/homework_lesson_6_joins_SOLUTION.ipynb"
notebook_path = "/Users/humphrjk/GitHub/ai-homework-grader-clean/data/raw/homework_lesson_6_joins_Michael_Alexander.ipynb"

print(f"✅ Using Assignment 6")
print(f"   Rubric: {rubric_path}")
print(f"   Solution: {solution_path}")
print(f"   Student: {notebook_path}")

print(f"\n🎓 Initializing grader...")
grader = BusinessAnalyticsGraderV2(
    rubric_path=rubric_path,
    solution_path=solution_path
)

print(f"\n📝 Grading: {notebook_path}")
print("="*80)

# Run validation only (faster test)
validation_results = grader._run_4layer_validation(notebook_path)

print(f"\n📊 RESULTS:")
print(f"Base Score: {validation_results['base_score']:.1f}%")
print(f"Adjusted Score: {validation_results['adjusted_score']:.1f}%")
print(f"Final Score: {(validation_results['adjusted_score']/100)*37.5:.1f}/37.5")

print(f"\n⏱️ TIMING:")
print(f"Validation Time: {grader.grading_stats.get('validation_time', 0):.1f}s")

print(f"\n✅ Grading test complete!")
