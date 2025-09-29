#!/usr/bin/env python3
"""
Test the rubric parsing fix
"""

import sys
import json
sys.path.append('.')

def test_create_grading_prompt():
    """Test the create_grading_prompt method with various rubric formats"""
    from ai_grader import AIGrader
    from app import HomeworkGrader
    
    print("🧪 Testing create_grading_prompt with different rubric formats")
    print("=" * 60)
    
    grader = HomeworkGrader()
    ai_grader = AIGrader(grader)
    
    # Test cases
    test_rubrics = [
        {
            "name": "Valid Dictionary Format",
            "rubric": {
                "environment_setup": {
                    "points": 5.5,
                    "description": "R/RStudio environment setup"
                },
                "package_management": {
                    "points": 5.5,
                    "description": "Package loading"
                }
            }
        },
        {
            "name": "Mixed Format (some strings)",
            "rubric": {
                "environment_setup": {
                    "points": 5.5,
                    "description": "R/RStudio environment setup"
                },
                "package_management": "Just a string value"
            }
        },
        {
            "name": "All Strings",
            "rubric": {
                "criterion1": "string value 1",
                "criterion2": "string value 2"
            }
        },
        {
            "name": "Empty Rubric",
            "rubric": {}
        }
    ]
    
    for test_case in test_rubrics:
        print(f"\n📝 Testing: {test_case['name']}")
        
        try:
            prompt = ai_grader.create_grading_prompt(
                assignment_name="Test Assignment",
                description="Test Description", 
                rubric=test_case['rubric'],
                student_code="# Test code\nprint('hello')",
                student_markdown="# Test markdown",
                solution_code="# Solution code"
            )
            
            print("   ✅ Prompt created successfully")
            print(f"   📏 Prompt length: {len(prompt)} characters")
            
            # Check if rubric section is in the prompt
            if "GRADING RUBRIC:" in prompt:
                print("   ✅ Rubric section included")
            else:
                print("   ⚠️  No rubric section (empty rubric)")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

def test_with_actual_rubric():
    """Test with the actual homework rubric file"""
    print(f"\n🎯 Testing with actual homework rubric")
    print("=" * 40)
    
    try:
        # Load the actual rubric
        with open('homework_1_simple_rubric.json', 'r') as f:
            rubric = json.load(f)
        
        from ai_grader import AIGrader
        from app import HomeworkGrader
        
        grader = HomeworkGrader()
        ai_grader = AIGrader(grader)
        
        prompt = ai_grader.create_grading_prompt(
            assignment_name="Homework 1 - R Environment Setup",
            description="Introduction to R and data import",
            rubric=rubric,
            student_code="library(tidyverse)\ndata <- read_csv('test.csv')",
            student_markdown="# My Analysis\nThis is my homework submission.",
            solution_code="# Solution code here"
        )
        
        print("✅ Actual rubric processed successfully")
        print(f"📏 Prompt length: {len(prompt)} characters")
        
        # Show a snippet of the rubric section
        if "GRADING RUBRIC:" in prompt:
            rubric_start = prompt.find("GRADING RUBRIC:")
            rubric_section = prompt[rubric_start:rubric_start+300]
            print(f"📋 Rubric section preview:\n{rubric_section}...")
        
    except Exception as e:
        print(f"❌ Error with actual rubric: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_create_grading_prompt()
    test_with_actual_rubric()
    
    print("\n" + "=" * 60)
    print("🎉 If all tests passed, the rubric parsing is fixed!")
    print("💡 The AI grader should now work without string errors.")