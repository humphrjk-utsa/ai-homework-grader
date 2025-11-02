#!/usr/bin/env python3
"""
Test complete grading system WITH MLX AI feedback
Uses existing Mac Studio infrastructure
"""

from validators.hybrid_grading_pipeline import HybridGradingPipeline
from pathlib import Path

print("="*80)
print("COMPLETE GRADING SYSTEM WITH MLX AI FEEDBACK")
print("="*80)
print("\nStudent: Kathryn Emerick (Emerickkathrynj)")
print("\nUsing:")
print("  - Mac Studio 1 (10.55.0.1:5001): GPT-OSS-120B")
print("  - Mac Studio 2 (10.55.0.2:5002): Qwen3-Coder-30B")
print()

# Initialize pipeline with MLX
pipeline = HybridGradingPipeline(
    solution_notebook_path="data/raw/homework_lesson_6_joins_SOLUTION.ipynb",
    rubric_path="rubrics/assignment_6_rubric.json",
    use_distributed_mlx=True
)

# Check server status
print("Checking server status...")
status = pipeline.mlx_client.get_system_status()
print(f"  Qwen (Mac Studio 2): {'✅ Online' if status['qwen_available'] else '❌ Offline'}")
print(f"  GPT-OSS (Mac Studio 1): {'✅ Online' if status['gemma_available'] else '❌ Offline'}")

if not status['distributed_ready']:
    print("\n⚠️ Warning: Not all servers are online!")
    print("   Run ./RESTART_NOW.sh to start servers")
    exit(1)

print("\n" + "="*80)
print("GRADING WITH AI ANALYSIS")
print("="*80)

# Grade submission
try:
    result = pipeline.grade_submission("submissions/12/Emerickkathrynj_emerickkathrynj.ipynb")
    
    # Generate comprehensive report
    output_dir = Path("grading_results_mlx")
    output_dir.mkdir(exist_ok=True)
    
    report_path = output_dir / "Emerickkathrynj_comprehensive_report.txt"
    pipeline.generate_comprehensive_report(result, str(report_path))
    
    print("\n" + "="*80)
    print("GRADING COMPLETE!")
    print("="*80)
    print(f"\nFinal Grade: {result['grade']} ({result['adjusted_score']:.1f}%)")
    print(f"Report saved to: {report_path}")
    
    # Show preview of AI feedback
    print("\n" + "="*80)
    print("AI FEEDBACK PREVIEW")
    print("="*80)
    
    if result.get('code_evaluation'):
        code_analysis = result['code_evaluation'].get('raw_response', '')
        if code_analysis and code_analysis != 'No response':
            print("\n[QWEN CODE ANALYSIS]")
            print(code_analysis[:500] + "..." if len(code_analysis) > 500 else code_analysis)
    
    if result.get('narrative_feedback'):
        feedback = result['narrative_feedback'].get('raw_response', '')
        if feedback and feedback != 'No response':
            print("\n[GPT-OSS FEEDBACK]")
            print(feedback[:500] + "..." if len(feedback) > 500 else feedback)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
