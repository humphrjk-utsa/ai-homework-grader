#!/usr/bin/env python3
"""
Test script to verify output comparison is working correctly
"""

import sys
sys.path.insert(0, '.')

from business_analytics_grader_v2 import BusinessAnalyticsGraderV2
import json

# Initialize grader
print("Initializing grader...")
grader = BusinessAnalyticsGraderV2(
    rubric_path='rubrics/midterm_exam_rubric_comprehensive.json',
    solution_path='data/raw/MIDTERM_EXAM_COMPREHENSIVE_SOLUTION.ipynb'
)

# Run validation on student submission
notebook_path = 'data/raw/cookwesleyc_176941_12009878_MIDTERM_EXAM_COMPREHENSIVE (1).ipynb'

print("\n" + "="*80)
print("TESTING OUTPUT COMPARISON INTEGRATION")
print("="*80)

# Run 4-layer validation
validation_results = grader._run_4layer_validation(notebook_path)

print("\n" + "="*80)
print("VALIDATION RESULTS:")
print("="*80)
print(f"Base score (systematic): {validation_results['base_score']:.1f}%")
print(f"Adjusted score (with output): {validation_results['adjusted_score']:.1f}%")
print(f"Max points: {grader.max_points}")
print(f"Final points: {(validation_results['adjusted_score']/100) * grader.max_points:.1f}")

if validation_results.get('output_results'):
    out = validation_results['output_results']
    print(f"\nOutput comparison:")
    print(f"  Match rate: {out['overall_match']*100:.1f}%")
    print(f"  Cells matched: {out['passed_checks']}/{out['total_checks']}")
    print(f"  Output score: {out.get('output_score', 0):.1f}%")
    
    # Show mismatches
    if out.get('discrepancies'):
        print(f"\n  Mismatched cells: {len(out['discrepancies'])}")
        for disc in out['discrepancies'][:3]:
            cell_idx = disc.get('cell_index', '?')
            reason = disc.get('reason', 'unknown')
            print(f"    - Cell {cell_idx}: {reason}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
print("\nExpected behavior:")
print("  ✓ Base score should be ~93.9% (systematic validation)")
print("  ✓ Output score should be ~91.3% (21/23 cells match)")
print("  ✓ Adjusted score should be ~92.6% (50/50 blend)")
print("  ✓ Final points should be ~115.8/125")
