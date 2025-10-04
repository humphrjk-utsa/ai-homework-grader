#!/usr/bin/env python3
"""
Test Natural Instructor-Like Feedback Generation
"""

from business_analytics_grader import BusinessAnalyticsGrader

def test_natural_feedback():
    """Test the improved feedback generation"""
    
    print("🧪 Testing Natural Instructor-Like Feedback")
    print("=" * 50)
    
    # Sample incomplete assignment (like the one described)
    student_code = '''
# Set up environment
getwd()
dir.create('outputs', showWarnings = FALSE)

# Install and load packages
library(tidyverse)
library(readxl)

# Import data (truncated)
sales_df <- read_excel('sales_data.xlsx')
'''

    student_markdown = '''
# Assignment 1: Data Exploration

## Part 1: Environment Setup
I set up my working directory and loaded the necessary packages.

## Part 2: Basic Data Inspection

### Observations for ratings_df:
The ratings dataset contains customer ratings from 1-5 scale with some missing values.

### Observations for comments_df:
The comments dataset has text feedback that will need preprocessing.

### Observations for sales_df:
[Placeholder - need to complete]

## Reflection Questions

### Question 1: Data Types Analysis
Date: should be a Date type. This is appropriate for time-based analysis (sorting by date, grouping by month/quarter, time series). 
Amount: should be numeric/double. This is appropriate for sums, averages, and other calculations used in sales analytics.

### Question 2: Data Quality Assessment
Date: should be a Date type. This is appropriate for time-based analysis (sorting by date, grouping by month/quarter, time series). 
Amount: should be numeric/double. This is appropriate for sums, averages, and other calculations used in sales analytics.

### Question 3: Analysis Readiness
The sales_df dataset looks the most ready for analysis because its values are mostly numeric and dates are already structured, making it easy to summarize and visualize. The dataset that needs the most preprocessing is comments_df because text data often has missing values, inconsistent formatting, and requires cleaning.

### Reflection Question 1:
Looking at the three datasets, I can see they are well-organized with clear column names. There are some missing values and the data types look mostly appropriate for analysis. The structure seems good for business analytics work.
'''
    
    grader = BusinessAnalyticsGrader()
    
    if not grader.use_distributed_mlx:
        print("❌ Distributed MLX not available - cannot test natural feedback")
        return False
    
    print("🚀 Generating natural instructor feedback...")
    
    try:
        result = grader.grade_submission(
            student_code=student_code,
            student_markdown=student_markdown,
            solution_code='# Complete solution with proper data exploration',
            assignment_info={'title': 'Assignment 1: Data Exploration'},
            rubric_elements={}
        )
        
        print(f"✅ Grading completed!")
        print(f"📊 Score: {result['final_score']}/37.5 ({result['final_score_percentage']:.1f}%)")
        
        # Display the natural feedback
        feedback = result.get('comprehensive_feedback', {})
        
        print(f"\n📝 Instructor Comments:")
        print("=" * 30)
        comments = feedback.get('instructor_comments', '')
        print(comments)
        
        print(f"\n🤔 Reflection Assessment:")
        print("=" * 30)
        detailed = feedback.get('detailed_feedback', {})
        reflection_assessment = detailed.get('reflection_assessment', [])
        for i, comment in enumerate(reflection_assessment[:2], 1):
            print(f"{i}. {comment}")
        
        print(f"\n💪 Analytical Strengths:")
        print("=" * 30)
        strengths = detailed.get('analytical_strengths', [])
        for i, strength in enumerate(strengths[:2], 1):
            print(f"{i}. {strength}")
        
        print(f"\n📈 Areas for Development:")
        print("=" * 30)
        areas = detailed.get('areas_for_development', [])
        for i, area in enumerate(areas[:2], 1):
            print(f"{i}. {area}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_natural_feedback()
    if success:
        print(f"\n🎉 Natural feedback test completed!")
        print(f"\n💡 Key Improvements:")
        print(f"• More conversational, instructor-like tone")
        print(f"• Specific, actionable feedback")
        print(f"• Focus on learning and growth")
        print(f"• Natural language instead of mechanical assessments")
    else:
        print(f"\n❌ Test failed - check system status")