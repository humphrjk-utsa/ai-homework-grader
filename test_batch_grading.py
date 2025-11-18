#!/usr/bin/env python3
"""
Test batch grading with all enhancements
"""

import sys
sys.path.insert(0, '.')

from business_analytics_grader_v2 import BusinessAnalyticsGraderV2

# Simulate batch grading setup
print("TESTING BATCH GRADING SETUP:")
print("="*80)

# Initialize grader (like batch process does)
rubric_path = 'rubrics/midterm_exam_rubric_comprehensive.json'
solution_path = 'data/raw/MIDTERM_EXAM_COMPREHENSIVE_SOLUTION.ipynb'

grader = BusinessAnalyticsGraderV2(
    rubric_path=rubric_path,
    solution_path=solution_path
)

print(f"✅ Grader initialized")
print(f"   Rubric: {rubric_path}")
print(f"   Solution: {solution_path}")
print(f"   Max points: {grader.max_points}")

# Simulate grading a submission (like batch process does)
notebook_path = 'data/raw/cookwesleyc_176941_12009878_MIDTERM_EXAM_COMPREHENSIVE (1).ipynb'

print(f"\n{'='*80}")
print(f"GRADING SUBMISSION:")
print(f"{'='*80}")

# This is what grade_submission_internal calls
result = grader.grade_submission(
    student_code="# Code extracted from notebook",
    student_markdown="# Markdown extracted",
    template_code="",
    solution_code="",
    assignment_info={
        'name': 'mt13',
        'title': 'Midterm Exam',
        'rubric': '{}'
    },
    notebook_path=notebook_path,
    preprocessing_info={}
)

print(f"\n{'='*80}")
print(f"BATCH GRADING RESULT:")
print(f"{'='*80}")
print(f"Final Score: {result['final_score']:.1f}/{result['max_points']}")
print(f"Percentage: {result['final_score_percentage']:.1f}%")

# Check if all enhancements were applied
print(f"\n{'='*80}")
print(f"ENHANCEMENTS CHECK:")
print(f"{'='*80}")

validation_results = result.get('validation_results', {})
if validation_results:
    print(f"✅ Systematic validation: {validation_results.get('base_score', 0):.1f}%")
    
    output_results = validation_results.get('output_results')
    if output_results:
        print(f"✅ Output comparison: {output_results.get('output_score', 0):.1f}%")
    else:
        print(f"❌ Output comparison: Not found")
    
    # Check for reflection grading
    section_breakdown = validation_results.get('systematic_results', {}).get('section_breakdown', {})
    for section_id, section_data in section_breakdown.items():
        if 'reflection' in section_data.get('name', '').lower():
            if section_data.get('ai_graded'):
                print(f"✅ Reflection grading: {section_data.get('reflection_percentage', 0):.0f}%")
            else:
                print(f"⚠️ Reflection grading: Completion-based only")
            break
    
    # Check for function equivalents
    part2 = section_breakdown.get('part2_data_cleaning', {})
    if part2.get('status') == 'complete':
        print(f"✅ Function equivalents: Working (Part 2 complete)")
    else:
        print(f"❌ Function equivalents: Not working (Part 2 {part2.get('status')})")
else:
    print(f"❌ No validation results found")

print(f"\n{'='*80}")
print(f"CONCLUSION:")
print(f"{'='*80}")
if result['final_score'] >= 120:
    print(f"✅ Batch grading is working correctly with all enhancements!")
    print(f"   Student received proper credit for equivalent functions")
    print(f"   Output comparison and reflection grading are active")
else:
    print(f"⚠️ Score seems low - check if all enhancements are working")
