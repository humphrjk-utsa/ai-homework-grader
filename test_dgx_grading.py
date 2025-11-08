#!/usr/bin/env python3
"""
Test grading on test-DGX branch
"""

import json
from business_analytics_grader_v2 import BusinessAnalyticsGraderV2

print("="*80)
print("TESTING GRADING ON TEST-DGX BRANCH")
print("="*80)

# Initialize grader
rubric_path = "rubrics/assignment_7_rubric_v2.json"
solution_path = "data/raw/homework_lesson_7_string_datetime_SOLUTION_v2.ipynb"

grader = BusinessAnalyticsGraderV2(
    rubric_path=rubric_path,
    solution_path=solution_path
)

# Test cases
test_cases = [
    {
        "name": "Low scorer (should not go negative)",
        "notebook": "submissions/16/Coronelmarcelom_coronelmarcelom.ipynb",
        "expected_range": (10, 15)
    },
    {
        "name": "High scorer (should get appropriate penalty)",
        "notebook": "data/raw/marccharlesanathaliaj_169558_11954692_Marc-Charles_Anathalia_homework_lesson_7_string_datetime.ipynb",
        "expected_range": (80, 90)
    },
    {
        "name": "Solution (should get ~99%)",
        "notebook": "data/raw/homework_lesson_7_string_datetime_SOLUTION_v2.ipynb",
        "expected_range": (95, 100)
    }
]

print("\n🧪 Running test cases...\n")

for i, test in enumerate(test_cases, 1):
    print(f"[Test {i}/3] {test['name']}")
    print(f"  Notebook: {test['notebook'].split('/')[-1]}")
    
    try:
        # Run validation
        validation_results = grader._run_4layer_validation(test['notebook'])
        
        base_score = validation_results['base_score']
        adjusted_score = validation_results['adjusted_score']
        final_score_37_5 = (adjusted_score / 100) * 37.5
        
        # Check if in expected range
        in_range = test['expected_range'][0] <= adjusted_score <= test['expected_range'][1]
        status = "✅ PASS" if in_range else "❌ FAIL"
        
        print(f"  Base Score: {base_score:.1f}%")
        print(f"  Adjusted Score: {adjusted_score:.1f}%")
        print(f"  Final Score: {final_score_37_5:.1f}/37.5")
        print(f"  Expected Range: {test['expected_range'][0]}-{test['expected_range'][1]}%")
        print(f"  {status}")
        
        # Check for negative scores
        if adjusted_score < 0:
            print(f"  ⚠️  WARNING: Negative score detected!")
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    print()

print("="*80)
print("✅ Test complete! Check results above.")
print("="*80)
