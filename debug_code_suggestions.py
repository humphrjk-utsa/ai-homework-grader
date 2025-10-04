#!/usr/bin/env python3
"""
Debug Code Suggestions in Reports
Check if code suggestions are being generated and included properly
"""

from business_analytics_grader import BusinessAnalyticsGrader
import json

def debug_code_suggestions():
    """Debug the code suggestions generation"""
    
    print("🔍 Debugging Code Suggestions Generation")
    print("=" * 50)
    
    grader = BusinessAnalyticsGrader()
    
    if not grader.use_distributed_mlx:
        print("❌ Distributed MLX not available")
        return
    
    # Simple test code
    student_code = '''
library(tidyverse)
library(readxl)

# Import data
sales_df <- read_excel("sales_data.xlsx")
ratings_df <- read.csv("ratings.csv")

# Basic exploration
head(sales_df)
str(sales_df)
summary(sales_df)
'''
    
    student_markdown = '''
# Assignment 1: Data Exploration

## Part 1: Environment Setup
I loaded the necessary packages and imported the datasets.

## Reflection Question 1:
The data looks well-organized and ready for analysis.
'''
    
    print("🚀 Testing code analysis generation...")
    
    try:
        result = grader.grade_submission(
            student_code=student_code,
            student_markdown=student_markdown,
            solution_code='# solution',
            assignment_info={'title': 'Debug Test'},
            rubric_elements={}
        )
        
        # Check technical analysis
        technical_analysis = result.get('technical_analysis', {})
        
        print(f"\n📊 Technical Analysis Keys: {list(technical_analysis.keys())}")
        
        code_strengths = technical_analysis.get('code_strengths', [])
        code_suggestions = technical_analysis.get('code_suggestions', [])
        technical_observations = technical_analysis.get('technical_observations', [])
        
        print(f"\n💪 Code Strengths ({len(code_strengths)}):")
        for i, strength in enumerate(code_strengths, 1):
            print(f"  {i}. {strength}")
        
        print(f"\n💡 Code Suggestions ({len(code_suggestions)}):")
        for i, suggestion in enumerate(code_suggestions, 1):
            print(f"  {i}. {suggestion}")
        
        print(f"\n🔍 Technical Observations ({len(technical_observations)}):")
        for i, obs in enumerate(technical_observations, 1):
            print(f"  {i}. {obs}")
        
        # Check if code suggestions are present
        if code_suggestions:
            print(f"\n✅ Code suggestions are present and should appear in reports!")
        else:
            print(f"\n❌ Code suggestions are missing!")
            
        # Show the raw technical analysis for debugging
        print(f"\n🔧 Raw Technical Analysis:")
        print(json.dumps(technical_analysis, indent=2))
        
        return len(code_suggestions) > 0
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_code_suggestions()
    if success:
        print(f"\n🎉 Code suggestions are working correctly!")
    else:
        print(f"\n❌ Code suggestions need investigation")