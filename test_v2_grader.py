#!/usr/bin/env python3
"""
Test BusinessAnalyticsGraderV2 with 4-layer validation
Verify it produces structured feedback in the correct format
"""

import json
from business_analytics_grader_v2 import BusinessAnalyticsGraderV2

print("="*80)
print("TESTING BUSINESS ANALYTICS GRADER V2")
print("4-Layer Validation + Structured Feedback")
print("="*80)
print()

# Initialize grader with rubric and solution
grader = BusinessAnalyticsGraderV2(
    rubric_path="rubrics/assignment_6_rubric.json",
    solution_path="data/raw/homework_lesson_6_joins_SOLUTION.ipynb"
)

print("\n" + "="*80)
print("GRADING TEST SUBMISSION")
print("="*80)

# Grade a submission
notebook_path = "submissions/12/Emerickkathrynj_emerickkathrynj.ipynb"

# Read notebook for code/markdown
with open(notebook_path, 'r') as f:
    notebook = json.load(f)

student_code = ""
student_markdown = ""
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        student_code += ''.join(cell['source']) + "\n\n"
    elif cell['cell_type'] == 'markdown':
        student_markdown += ''.join(cell['source']) + "\n\n"

# Grade the submission
result = grader.grade_submission(
    student_code=student_code,
    student_markdown=student_markdown,
    notebook_path=notebook_path,
    assignment_info={
        'name': 'Assignment 6: Joins',
        'title': 'Homework - Lesson 6: Combining Datasets - Joins'
    }
)

print("\n" + "="*80)
print("GRADING RESULTS")
print("="*80)

print(f"\n📊 SCORE:")
print(f"   Final Score: {result['final_score']:.1f}/{result['max_points']}")
print(f"   Percentage: {result['final_score_percentage']:.1f}%")

print(f"\n📝 INSTRUCTOR COMMENTS:")
print(f"   {result['comprehensive_feedback']['instructor_comments']}")

print(f"\n✅ STRUCTURED FEEDBACK SECTIONS:")
detailed = result['comprehensive_feedback']['detailed_feedback']
for section_name, section_content in detailed.items():
    print(f"   - {section_name}: {len(section_content)} items")

print(f"\n🔧 TECHNICAL ANALYSIS SECTIONS:")
tech = result['technical_analysis']
for section_name, section_content in tech.items():
    print(f"   - {section_name}: {len(section_content)} items")

print(f"\n" + "="*80)
print("DETAILED FEEDBACK PREVIEW")
print("="*80)

print(f"\n🤔 Reflection Assessment:")
for item in detailed['reflection_assessment']:
    print(f"   • {item}")

print(f"\n💪 Analytical Strengths:")
for item in detailed['analytical_strengths'][:3]:  # Show first 3
    print(f"   • {item}")

print(f"\n🎯 Areas for Development:")
for item in detailed['areas_for_development'][:2]:  # Show first 2
    print(f"   {item}")

print(f"\n💡 Recommendations:")
for item in detailed['recommendations']:
    print(f"   • {item}")

print(f"\n" + "="*80)
print("TECHNICAL ANALYSIS PREVIEW")
print("="*80)

print(f"\n✅ Code Strengths:")
for item in tech['code_strengths'][:3]:  # Show first 3
    print(f"   • {item}")

print(f"\n🔧 Code Improvement Suggestions:")
for item in tech['code_suggestions'][:2]:  # Show first 2
    print(f"   {item}")

print(f"\n📊 Technical Observations:")
for item in tech['technical_observations']:
    print(f"   • {item}")

print(f"\n" + "="*80)
print("VALIDATION RESULTS")
print("="*80)

val_results = result['validation_results']
sys_result = val_results['systematic_results']
output_result = val_results.get('output_results')

print(f"\nSystematic Validation:")
print(f"   Variables: {sys_result['variable_check']['found']}/{sys_result['variable_check']['total_required']}")
print(f"   Execution: {sys_result['cell_stats']['execution_rate']*100:.1f}%")
print(f"   Base Score: {sys_result['final_score']:.1f}/100")

if output_result:
    print(f"\nOutput Validation:")
    print(f"   Match Rate: {output_result['overall_match']*100:.1f}%")
    print(f"   Checks Passed: {output_result['passed_checks']}/{output_result['total_checks']}")
    print(f"   Score Adjustment: {output_result['score_adjustment']:+.1f}")

print(f"\n" + "="*80)
print("VERIFICATION CHECKLIST")
print("="*80)

# Verify all required sections are present
required_sections = {
    'comprehensive_feedback': ['instructor_comments', 'detailed_feedback'],
    'detailed_feedback': ['reflection_assessment', 'analytical_strengths', 'business_application', 
                          'areas_for_development', 'recommendations'],
    'technical_analysis': ['code_strengths', 'code_suggestions', 'technical_observations']
}

all_present = True
for parent, sections in required_sections.items():
    if parent == 'detailed_feedback':
        parent_obj = result['comprehensive_feedback']['detailed_feedback']
    elif parent == 'comprehensive_feedback':
        parent_obj = result['comprehensive_feedback']
    else:
        parent_obj = result[parent]
    
    for section in sections:
        if section in parent_obj:
            print(f"   ✅ {section}")
        else:
            print(f"   ❌ {section} MISSING!")
            all_present = False

print(f"\n" + "="*80)
if all_present:
    print("✅ SUCCESS! All required sections present.")
    print("✅ Structured feedback format maintained.")
    print("✅ 4-layer validation integrated successfully.")
else:
    print("❌ FAILURE! Some required sections are missing.")
print("="*80)

# Save full result to file for inspection
with open('test_v2_grader_output.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\n💾 Full results saved to: test_v2_grader_output.json")
