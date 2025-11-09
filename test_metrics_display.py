#!/usr/bin/env python3
"""Test if metrics are properly captured and displayed"""

from business_analytics_grader import BusinessAnalyticsGrader
from disaggregated_client import DisaggregatedClient
import json

# Initialize disaggregated client
disagg_client = DisaggregatedClient()

# Initialize grader with disaggregated client
grader = BusinessAnalyticsGrader(disaggregated_client=disagg_client)

# Load rubric
with open('rubrics/assignment_7_rubric_v2.json', 'r') as f:
    rubric = json.load(f)

# Grade a test notebook
print("🚀 Grading test notebook...")
result = grader.grade_notebook(
    'data/raw/homework_lesson_7_string_datetime_SOLUTION_v2.ipynb',
    rubric
)

print("\n" + "="*80)
print("📊 CHECKING PERFORMANCE DIAGNOSTICS")
print("="*80)

# Check if performance_diagnostics exists
if 'performance_diagnostics' in result:
    print('✅ performance_diagnostics found in result')
    perf = result['performance_diagnostics']
    print(f'Keys: {list(perf.keys())}')
    
    if 'qwen_performance' in perf:
        print(f'\n✅ qwen_performance:')
        for k, v in perf['qwen_performance'].items():
            print(f'   {k}: {v}')
    else:
        print('\n❌ qwen_performance NOT found')
    
    if 'gemma_performance' in perf:
        print(f'\n✅ gemma_performance:')
        for k, v in perf['gemma_performance'].items():
            print(f'   {k}: {v}')
    else:
        print('\n❌ gemma_performance NOT found')
        
    if 'combined_metrics' in perf:
        print(f'\n✅ combined_metrics:')
        for k, v in perf['combined_metrics'].items():
            print(f'   {k}: {v}')
    else:
        print('\n❌ combined_metrics NOT found')
else:
    print('❌ performance_diagnostics NOT found in result')
    print(f'Available keys: {list(result.keys())}')
