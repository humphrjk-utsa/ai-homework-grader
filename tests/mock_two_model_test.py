#!/usr/bin/env python3
"""
Mock test of two-model system without heavy model loading
"""

import time
import sys
sys.path.append('.')

class MockMLXClient:
    """Mock MLX client that simulates responses without loading models"""
    
    def __init__(self, model_name):
        self.model_name = model_name
        print(f"🎭 Mock client initialized: {model_name}")
    
    def generate_response(self, prompt, max_tokens=2000):
        """Mock response generation"""
        time.sleep(2)  # Simulate processing time
        
        if "code" in self.model_name.lower() or "qwen" in self.model_name.lower():
            # Mock code analysis response
            return """
            **Code Analysis:**
            - The R code is syntactically correct
            - Uses read.csv() for data import - ✅ Good
            - Uses summary() for data exploration - ✅ Good
            - Missing error handling for file not found
            - Score: 85/100
            """
        else:
            # Mock feedback response
            return """
            **Educational Feedback:**
            Great work on your R code! You've successfully demonstrated:
            
            ✅ **Strengths:**
            - Proper use of read.csv() function
            - Good data exploration with summary()
            - Clean, readable code structure
            
            💡 **Suggestions for improvement:**
            - Consider adding error handling
            - Try exploring with head() and str() functions
            
            **Overall:** Excellent foundation! Score: 94%
            """

def test_mock_two_model_system():
    """Test the two-model workflow with mock clients"""
    
    print("🎭 Mock Two-Model System Test")
    print("=" * 50)
    
    # Mock the MLX clients
    print("🔧 Initializing mock models...")
    code_analyzer = MockMLXClient("mlx-community/Qwen3-Coder-30B-A3B-Instruct-bf16")
    feedback_generator = MockMLXClient("mlx-community/gemma-3-27b-it-bf16")
    
    # Test data
    student_code = """
    # Load data
    data <- read.csv("homework_data.csv")
    
    # Explore data
    summary(data)
    head(data)
    """
    
    # Step 1: Code Analysis
    print("\n📊 Step 1: Code Analysis")
    start_analysis = time.time()
    
    analysis_prompt = f"""
    Analyze this R code for correctness and completeness:
    
    {student_code}
    
    Provide technical analysis and scoring.
    """
    
    analysis_result = code_analyzer.generate_response(analysis_prompt)
    analysis_time = time.time() - start_analysis
    
    print(f"⏱️  Analysis time: {analysis_time:.1f}s")
    print(f"📄 Analysis result: {analysis_result[:100]}...")
    
    # Step 2: Feedback Generation
    print("\n📝 Step 2: Educational Feedback")
    start_feedback = time.time()
    
    feedback_prompt = f"""
    Based on this code analysis, provide encouraging educational feedback:
    
    Student Code:
    {student_code}
    
    Analysis:
    {analysis_result}
    
    Provide supportive feedback for a business analytics student.
    """
    
    feedback_result = feedback_generator.generate_response(feedback_prompt)
    feedback_time = time.time() - start_feedback
    
    print(f"⏱️  Feedback time: {feedback_time:.1f}s")
    print(f"📄 Feedback result: {feedback_result[:100]}...")
    
    # Summary
    total_time = analysis_time + feedback_time
    print(f"\n🎯 MOCK SYSTEM PERFORMANCE")
    print("=" * 50)
    print(f"📊 Code Analysis: {analysis_time:.1f}s")
    print(f"📝 Feedback Generation: {feedback_time:.1f}s")
    print(f"⏱️  Total Time: {total_time:.1f}s")
    
    if total_time < 10:
        print("🚀 EXCELLENT: Very fast workflow!")
    elif total_time < 30:
        print("✅ GOOD: Reasonable workflow speed")
    else:
        print("⚠️  SLOW: Workflow needs optimization")
    
    print(f"\n📈 Estimated real performance with bf16 models:")
    print(f"   Code Analysis: ~60-90s")
    print(f"   Feedback Generation: ~60-90s") 
    print(f"   Total: ~120-180s per submission")
    
    return {
        'analysis_time': analysis_time,
        'feedback_time': feedback_time,
        'total_time': total_time,
        'analysis_result': analysis_result,
        'feedback_result': feedback_result
    }

if __name__ == "__main__":
    test_mock_two_model_system()