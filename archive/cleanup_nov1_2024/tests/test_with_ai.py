#!/usr/bin/env python3
"""
Test complete grading system WITH AI feedback
"""

from validators.hybrid_grading_pipeline import HybridGradingPipeline
from pathlib import Path

print("="*80)
print("COMPLETE GRADING SYSTEM WITH AI FEEDBACK")
print("="*80)
print("\nStudent: Kathryn Emerick (Emerickkathrynj)")
print()

# Initialize pipeline
pipeline = HybridGradingPipeline(
    solution_notebook_path="data/raw/homework_lesson_6_joins_SOLUTION.ipynb",
    rubric_path="rubrics/assignment_6_rubric.json",
    qwen_endpoint="http://localhost:11434/api/generate",
    gpt_endpoint="http://localhost:11434/api/generate",
    qwen_model="qwen2.5-coder:latest",
    gpt_model="gpt-oss-120b:latest"
)

# Grade submission
try:
    result = pipeline.grade_submission("submissions/12/Emerickkathrynj_emerickkathrynj.ipynb")
    
    # Generate comprehensive report
    output_dir = Path("grading_results_with_ai")
    output_dir.mkdir(exist_ok=True)
    
    report_path = output_dir / "Emerickkathrynj_comprehensive_report.txt"
    pipeline.generate_comprehensive_report(result, str(report_path))
    
    print("\n" + "="*80)
    print("GRADING COMPLETE!")
    print("="*80)
    print(f"\nFinal Grade: {result['grade']} ({result['adjusted_score']:.1f}%)")
    print(f"Report saved to: {report_path}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
