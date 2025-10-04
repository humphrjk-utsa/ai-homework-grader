#!/usr/bin/env python3
"""
Test Performance Diagnostics
Verify that tokens per second and prompt evaluation metrics are captured
"""

from business_analytics_grader import BusinessAnalyticsGrader
import json
import time

def test_performance_diagnostics():
    """Test performance diagnostics capture"""
    
    print("🧪 Testing Performance Diagnostics")
    print("=" * 50)
    
    # Initialize grader
    grader = BusinessAnalyticsGrader()
    
    if not grader.use_distributed_mlx:
        print("❌ Distributed MLX not available, cannot test performance diagnostics")
        return
    
    # Simple test submission
    student_code = """
library(dplyr)
library(ggplot2)
data <- read.csv("test.csv")
summary(data)
plot(data$x, data$y)
"""
    
    student_markdown = """
# Test Analysis
This is a simple test analysis.

[What did you learn?] I learned basic R programming.
[How could this be improved?] Add more statistical analysis.
"""
    
    assignment_info = {
        'title': 'Performance Test Assignment',
        'name': 'Performance Test',
        'description': 'Testing performance diagnostics'
    }
    
    rubric_elements = {}
    
    print("🚀 Starting performance diagnostic test...")
    start_time = time.time()
    
    try:
        # Grade the submission
        result = grader.grade_submission(
            student_code=student_code,
            student_markdown=student_markdown,
            solution_code="# solution code",
            assignment_info=assignment_info,
            rubric_elements=rubric_elements
        )
        
        total_time = time.time() - start_time
        
        print(f"\n✅ Test completed in {total_time:.1f}s")
        
        # Check for performance diagnostics
        perf_diag = result.get('performance_diagnostics', {})
        
        if perf_diag:
            print(f"\n📊 Performance Diagnostics Found:")
            print(f"   Timestamp: {perf_diag.get('timestamp', 'N/A')}")
            
            # Qwen performance
            qwen_perf = perf_diag.get('qwen_performance', {})
            print(f"\n🔧 Qwen (Code Analysis) Performance:")
            print(f"   Model: {qwen_perf.get('model', 'N/A')}")
            print(f"   Server: {qwen_perf.get('server', 'N/A')}")
            print(f"   Prompt Tokens: {qwen_perf.get('prompt_tokens', 0)}")
            print(f"   Output Tokens: {qwen_perf.get('output_tokens', 0)}")
            print(f"   Total Tokens: {qwen_perf.get('total_tokens', 0)}")
            print(f"   Generation Time: {qwen_perf.get('generation_time_seconds', 0):.2f}s")
            print(f"   Tokens/Second: {qwen_perf.get('tokens_per_second', 0):.1f}")
            print(f"   Prompt Eval Time: {qwen_perf.get('prompt_eval_time_seconds', 0):.2f}s")
            
            # GPT-OSS performance
            gemma_perf = perf_diag.get('gemma_performance', {})
            print(f"\n📝 GPT-OSS (Feedback) Performance:")
            print(f"   Model: {gemma_perf.get('model', 'N/A')}")
            print(f"   Server: {gemma_perf.get('server', 'N/A')}")
            print(f"   Prompt Tokens: {gemma_perf.get('prompt_tokens', 0)}")
            print(f"   Output Tokens: {gemma_perf.get('output_tokens', 0)}")
            print(f"   Total Tokens: {gemma_perf.get('total_tokens', 0)}")
            print(f"   Generation Time: {gemma_perf.get('generation_time_seconds', 0):.2f}s")
            print(f"   Tokens/Second: {gemma_perf.get('tokens_per_second', 0):.1f}")
            print(f"   Prompt Eval Time: {gemma_perf.get('prompt_eval_time_seconds', 0):.2f}s")
            
            # Combined metrics
            combined = perf_diag.get('combined_metrics', {})
            print(f"\n🚀 Combined Performance:")
            print(f"   Total Tokens Processed: {combined.get('total_tokens_processed', 0)}")
            print(f"   Total Output Tokens: {combined.get('total_output_tokens', 0)}")
            print(f"   Parallel Efficiency: {combined.get('parallel_efficiency', 0):.1f}x")
            print(f"   Combined Throughput: {combined.get('combined_throughput_tokens_per_second', 0):.1f} tok/s")
            
            # Validation checks
            qwen_tps = qwen_perf.get('tokens_per_second', 0)
            gemma_tps = gemma_perf.get('tokens_per_second', 0)
            
            print(f"\n✅ Validation Results:")
            if qwen_tps > 0:
                print(f"   ✅ Qwen tokens/second captured: {qwen_tps:.1f}")
            else:
                print(f"   ❌ Qwen tokens/second missing")
            
            if gemma_tps > 0:
                print(f"   ✅ GPT-OSS tokens/second captured: {gemma_tps:.1f}")
            else:
                print(f"   ❌ GPT-OSS tokens/second missing")
            
            if qwen_perf.get('prompt_eval_time_seconds', 0) > 0:
                print(f"   ✅ Prompt evaluation time captured")
            else:
                print(f"   ❌ Prompt evaluation time missing")
            
            return True
        else:
            print("❌ No performance diagnostics found in result")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_performance_diagnostics()
    if success:
        print("\n🎉 Performance diagnostics test passed!")
    else:
        print("\n❌ Performance diagnostics test failed.")