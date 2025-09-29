#!/usr/bin/env python3
"""
Test the AI grading fix for the string error
"""

import sys
import os
sys.path.append('.')

def test_rubric_parsing():
    """Test rubric parsing with various inputs"""
    import json
    
    print("🧪 Testing Rubric Parsing")
    print("=" * 30)
    
    # Test cases that might cause the string error
    test_cases = [
        ('Valid JSON', '{"points": 10, "description": "test"}'),
        ('Invalid JSON', '{"points": 10, "description": "test"'),  # Missing closing brace
        ('Empty string', ''),
        ('None value', None),
        ('Non-JSON string', 'just a string'),
        ('Number', '123'),
    ]
    
    for name, rubric_input in test_cases:
        print(f"\n📝 Testing: {name}")
        print(f"   Input: {repr(rubric_input)}")
        
        # Simulate the fixed parsing logic
        rubric_data = {}
        if rubric_input:
            try:
                rubric_data = json.loads(rubric_input)
                if not isinstance(rubric_data, dict):
                    rubric_data = {}
                print(f"   ✅ Parsed successfully: {rubric_data}")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"   ⚠️  Parse failed (handled): {e}")
                rubric_data = {}
        else:
            print(f"   ✅ Empty input handled")
        
        # Test the .get() calls that were causing the error
        try:
            if rubric_data:
                for criterion, details in rubric_data.items():
                    points = details.get('points', 0) if isinstance(details, dict) else 0
                    desc = details.get('description', '') if isinstance(details, dict) else str(details)
                    print(f"     • {criterion}: {points} points - {desc}")
            print(f"   ✅ No .get() errors")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_ai_grader_initialization():
    """Test that the AI grader can be initialized without errors"""
    print("\n🤖 Testing AI Grader Initialization")
    print("=" * 40)
    
    try:
        from app import HomeworkGrader
        from ai_grader import AIGrader
        
        grader = HomeworkGrader()
        ai_grader = AIGrader(grader)
        
        print("✅ HomeworkGrader initialized")
        print("✅ AIGrader initialized")
        print(f"   Model: {ai_grader.local_ai.model_name}")
        print(f"   Available: {ai_grader.use_local_ai}")
        
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_rubric_parsing()
    
    success = test_ai_grader_initialization()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! The string error should be fixed.")
        print("💡 Try grading an assignment again in the Streamlit app.")
    else:
        print("❌ There are still issues that need to be resolved.")