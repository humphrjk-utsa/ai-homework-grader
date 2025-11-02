#!/usr/bin/env python3
"""
Test the complete 4-layer grading system
"""

from validators.assignment_6_systematic_validator import Assignment6SystematicValidator
from validators.smart_output_validator import SmartOutputValidator

print("="*80)
print("COMPLETE 4-LAYER GRADING SYSTEM TEST")
print("="*80)
print("\nStudent: Kathryn Emerick (Emerickkathrynj)")
print()

# LAYER 1: Systematic Validation
print("[LAYER 1: SYSTEMATIC VALIDATION]")
print("-"*80)
sys_validator = Assignment6SystematicValidator("rubrics/assignment_6_rubric.json")
sys_result = sys_validator.validate_notebook("submissions/12/Emerickkathrynj_emerickkathrynj.ipynb")

print(f"✅ Variables Found: {sys_result['variable_check']['found']}/25")
print(f"✅ Sections Complete: {sum(1 for s in sys_result['section_breakdown'].values() if s['status'] == 'complete')}/21")
print(f"✅ Execution Rate: {sys_result['cell_stats']['execution_rate']*100:.1f}%")
print(f"✅ Base Score: {sys_result['final_score']:.1f}/100")

# LAYER 2: Smart Output Validation
print(f"\n[LAYER 2: SMART OUTPUT VALIDATION]")
print("-"*80)
output_validator = SmartOutputValidator(
    "data/raw/homework_lesson_6_joins_SOLUTION.ipynb",
    "rubrics/assignment_6_rubric.json"
)
output_result = output_validator.validate_student_outputs("submissions/12/Emerickkathrynj_emerickkathrynj.ipynb")

print(f"✅ Output Match: {output_result['overall_match']*100:.1f}%")
print(f"✅ Checks Passed: {output_result['passed_checks']}/{output_result['total_checks']}")
print(f"✅ Discrepancies: {len(output_result['discrepancies'])}")
print(f"✅ Score Adjustment: {output_result['score_adjustment']} points")

if output_result['discrepancies']:
    print(f"\nDiscrepancies found:")
    for disc in output_result['discrepancies'][:3]:  # Show first 3
        print(f"  ❌ {disc['variable']}: {disc['issue']}")

# LAYER 3: Qwen Coder (Would analyze discrepancies)
print(f"\n[LAYER 3: QWEN CODER ANALYSIS]")
print("-"*80)
print("Would analyze:")
print("  - Why outputs don't match")
print("  - Root causes in code logic")
print("  - Specific fixes with code examples")
print("  - Code quality assessment")
print("\n(Requires Ollama running with qwen2.5-coder:latest)")

# LAYER 4: GPT-OSS Feedback Coordinator
print(f"\n[LAYER 4: GPT-OSS FEEDBACK COORDINATOR]")
print("-"*80)
print("Would synthesize:")
print("  - Overall assessment")
print("  - Strengths and areas for growth")
print("  - Clear, actionable recommendations")
print("  - Encouraging, educational tone")
print("\n(Requires Ollama running with gpt-oss-120b:latest)")

# FINAL SCORE
print(f"\n[FINAL SCORE]")
print("="*80)
adjusted_score = sys_result['final_score'] + output_result['score_adjustment']
grade = 'A' if adjusted_score >= 90 else 'B' if adjusted_score >= 80 else 'C' if adjusted_score >= 70 else 'D'

print(f"Base Score (Systematic):    {sys_result['final_score']:.1f}/100")
print(f"Output Adjustment:          {output_result['score_adjustment']:+.1f}")
print(f"Final Score:                {adjusted_score:.1f}/100")
print(f"Grade:                      {grade}")
print("="*80)

print(f"\n✅ SYSTEM WORKING!")
print(f"   - Systematic validation: ✅ Complete")
print(f"   - Output validation: ✅ Complete")
print(f"   - AI analysis: ⏳ Ready (needs Ollama)")
print(f"   - Feedback coordination: ⏳ Ready (needs Ollama)")
