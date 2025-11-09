#!/usr/bin/env python3
"""
Test the grader with disaggregated system
"""
from business_analytics_grader_v2 import BusinessAnalyticsGraderV2
from submission_preprocessor import SubmissionPreprocessor
import json

def test_grading():
    print('='*80)
    print('TESTING DISAGGREGATED SYSTEM WITH REAL GRADING')
    print('='*80)
    
    # Initialize grader
    grader = BusinessAnalyticsGraderV2(
        rubric_path='rubrics/assignment_6_rubric.json',
        solution_path='data/raw/homework_lesson_6_joins_SOLUTION.ipynb'
    )
    
    # Preprocess notebook
    print('\nPreprocessing notebook...')
    preprocessor = SubmissionPreprocessor()
    notebook_path = 'data/raw/homework_lesson_6_joins_Michael_Alexander.ipynb'
    
    student_code, student_markdown, fixes = preprocessor.preprocess_notebook(notebook_path)
    preprocessing_result = {
        'success': True,
        'student_code': student_code,
        'student_markdown': student_markdown,
        'fixes': fixes,
        'code_cells': [],
        'markdown_cells': []
    }
    
    if not preprocessing_result['success']:
        print(f"❌ Preprocessing failed: {preprocessing_result.get('error')}")
        return
    
    print(f"✅ Preprocessing successful")
    print(f"   Code length: {len(student_code)} chars")
    print(f"   Markdown length: {len(student_markdown)} chars")
    print(f"   Fixes applied: {len(fixes)}")
    
    # Grade the submission
    print('\nGrading submission...')
    print('-'*80)
    
    result = grader.grade_submission(
        student_code=preprocessing_result['student_code'],
        student_markdown=preprocessing_result['student_markdown'],
        template_code="",
        solution_code="",
        assignment_info={'assignment_name': 'Assignment 6 - SQL Joins'},
        notebook_path=notebook_path,
        preprocessing_info=preprocessing_result
    )
    
    print('\n' + '='*80)
    print('GRADING RESULTS')
    print('='*80)
    print(f"Student: Michael Alexander")
    print(f"Final Score: {result['final_score']:.1f}/100")
    print(f"Total Time: {grader.grading_stats['total_time']:.1f}s")
    
    # Check if disaggregated system was used
    print('\n' + '='*80)
    print('DISAGGREGATED SYSTEM METRICS')
    print('='*80)
    
    if 'qwen_metrics' in grader.grading_stats:
        qwen_metrics = grader.grading_stats['qwen_metrics']
        print('\n[QWEN - Code Analysis]')
        print('-'*80)
        if 'method' in qwen_metrics:
            print(f"Method: {qwen_metrics['method']}")
            if qwen_metrics['method'] == 'disaggregated':
                print(f"✅ Using Disaggregated Inference!")
                print(f"   Prefill Server: {qwen_metrics.get('prefill_server', 'N/A')}")
                print(f"   Decode Server: {qwen_metrics.get('decode_server', 'N/A')}")
                print(f"   Prefill Time: {qwen_metrics.get('prefill_time', 0):.2f}s")
                print(f"   Decode Time: {qwen_metrics.get('decode_time', 0):.2f}s")
                print(f"   Prefill Speed: {qwen_metrics.get('prefill_tokens_per_second', 0):.1f} tok/s")
                print(f"   Decode Speed: {qwen_metrics.get('decode_tokens_per_second', 0):.1f} tok/s")
                print(f"   Total Tokens: {qwen_metrics.get('total_tokens', 0)}")
    
    if 'gemma_metrics' in grader.grading_stats:
        gemma_metrics = grader.grading_stats['gemma_metrics']
        print('\n[GPT-OSS - Feedback Generation]')
        print('-'*80)
        if 'method' in gemma_metrics:
            print(f"Method: {gemma_metrics['method']}")
            if gemma_metrics['method'] == 'disaggregated':
                print(f"✅ Using Disaggregated Inference!")
                print(f"   Prefill Server: {gemma_metrics.get('prefill_server', 'N/A')}")
                print(f"   Decode Server: {gemma_metrics.get('decode_server', 'N/A')}")
                print(f"   Prefill Time: {gemma_metrics.get('prefill_time', 0):.2f}s")
                print(f"   Decode Time: {gemma_metrics.get('decode_time', 0):.2f}s")
                print(f"   Prefill Speed: {gemma_metrics.get('prefill_tokens_per_second', 0):.1f} tok/s")
                print(f"   Decode Speed: {gemma_metrics.get('decode_tokens_per_second', 0):.1f} tok/s")
                print(f"   Total Tokens: {gemma_metrics.get('total_tokens', 0)}")
    
    print('\n' + '='*80)
    print('TIMING BREAKDOWN')
    print('='*80)
    print(f"Validation: {grader.grading_stats.get('validation_time', 0):.1f}s")
    print(f"Code Analysis: {grader.grading_stats.get('code_analysis_time', 0):.1f}s")
    print(f"Feedback Generation: {grader.grading_stats.get('feedback_generation_time', 0):.1f}s")
    print(f"Total: {grader.grading_stats.get('total_time', 0):.1f}s")
    
    print('\n' + '='*80)
    print('✅ DISAGGREGATED GRADING TEST COMPLETE')
    print('='*80)
    
    # Save result
    with open('test_grading_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    print('\n📄 Full result saved to: test_grading_result.json')

if __name__ == '__main__':
    test_grading()
