#!/usr/bin/env python3
"""
Debug validator on the problematic submission
"""

import json
from validators.rubric_driven_validator import RubricDrivenValidator

# Initialize validator
rubric_path = "rubrics/assignment_7_rubric_v2.json"
#notebook_path = "submissions/16/Coronelmarcelom_coronelmarcelom.ipynb"
notebook_path = "data/raw/homework_lesson_7_string_datetime_SOLUTION_v2.ipynb"  # Test on solution

print("="*80)
print("TESTING VALIDATOR ON PROBLEMATIC SUBMISSION")
print("="*80)

validator = RubricDrivenValidator(rubric_path)

print(f"\n📋 Rubric: {rubric_path}")
print(f"📓 Notebook: {notebook_path}")

# Run validation
result = validator.validate_notebook(notebook_path)

print(f"\n🎯 VALIDATION RESULTS:")
print(f"Final Score: {result['final_score']:.1f}/100")
print(f"Variables Found: {result['variable_check']['found']}/{result['variable_check']['total_required']}")

print(f"\n📊 SECTION BREAKDOWN:")
for section_id, section_data in result['section_breakdown'].items():
    status_icon = "✅" if section_data['status'] == 'complete' else "❌"
    points_earned = section_data.get('points_earned', section_data.get('score', 0))
    points_possible = section_data.get('points_possible', section_data.get('points', 0))
    print(f"{status_icon} {section_data['name']}: {points_earned:.1f}/{points_possible} points ({section_data['status']})")
    print(f"   DEBUG: keys in section_data: {list(section_data.keys())}")
    print(f"   DEBUG: score={section_data.get('score')}, points={section_data.get('points')}")

print(f"\n📈 CELL STATS:")
print(f"Execution Rate: {result['cell_stats']['execution_rate']*100:.1f}%")
print(f"Total Cells: {result['cell_stats']['total_cells']}")
print(f"Executed Cells: {result['cell_stats']['executed_cells']}")

print("\n" + "="*80)
