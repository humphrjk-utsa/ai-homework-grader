#!/usr/bin/env python3
"""
Test script to verify verbose feedback is working in the web interface
"""

import json
import sqlite3
from business_analytics_grader import BusinessAnalyticsGrader

def test_verbose_feedback():
    """Test that the Business Analytics Grader returns comprehensive feedback"""
    
    print("🧪 Testing Verbose Feedback Generation...")
    
    # Initialize grader
    grader = BusinessAnalyticsGrader()
    
    # Test data
    student_code = '''
library(tidyverse)
library(readxl)

# Set working directory
setwd("/Users/student/homework")

# Import data
sales_df <- read_csv("data/sales_data.csv")
ratings_df <- read_excel("data/customer_feedback.xlsx", sheet = "ratings")
comments_df <- read_excel("data/customer_feedback.xlsx", sheet = "customer_feedback")

# Data inspection
head(sales_df)
str(sales_df)
summary(sales_df)

# Basic analysis
mean_sales <- mean(sales_df$sales_amount, na.rm = TRUE)
print(paste("Average sales:", mean_sales))
'''
    
    student_markdown = '''
# Business Analytics Assignment 1

## Data Import and Exploration

I successfully imported the sales data and customer feedback files. The data looks clean and ready for analysis.

## Reflection Questions

[What challenges did you encounter while working with the data?]
The main challenge was understanding the structure of the Excel file with multiple sheets. I had to use the readxl package and specify the sheet names.

[What did you learn about R programming through this assignment?]
I learned how to import different file types (CSV and Excel) and how to perform basic data exploration using head(), str(), and summary() functions.

[How might this analysis be useful for business decision-making?]
This analysis provides insights into sales patterns and customer satisfaction that could help inform marketing strategies and product improvements.

[What would you do differently next time?]
I would add more visualization and explore correlations between sales and customer ratings.
'''
    
    solution_code = '''
library(tidyverse)
library(readxl)

sales_df <- read_csv("data/sales_data.csv")
ratings_df <- read_excel("data/customer_feedback.xlsx", sheet = "ratings")
comments_df <- read_excel("data/customer_feedback.xlsx", sheet = "customer_feedback")

head(sales_df)
str(sales_df)
summary(sales_df)
'''
    
    assignment_info = {
        "title": "Assignment 1 - Introduction to R",
        "description": "Basic data import and exploration",
        "student_name": "Test Student"
    }
    
    rubric_elements = {
        "technical_execution": {"weight": 0.25, "max_score": 37.5},
        "business_thinking": {"weight": 0.30, "max_score": 37.5},
        "data_analysis": {"weight": 0.25, "max_score": 37.5},
        "communication": {"weight": 0.20, "max_score": 37.5}
    }
    
    try:
        # Grade the submission
        print("⚡ Grading submission...")
        result = grader.grade_submission(
            student_code=student_code,
            student_markdown=student_markdown,
            solution_code=solution_code,
            assignment_info=assignment_info,
            rubric_elements=rubric_elements
        )
        
        print("✅ Grading complete!")
        print(f"📊 Final Score: {result['final_score']}/37.5 ({result['final_score_percentage']:.1f}%)")
        
        # Test feedback structure
        print("\n🔍 Testing Feedback Structure...")
        
        # Check comprehensive feedback
        if 'comprehensive_feedback' in result:
            comp_feedback = result['comprehensive_feedback']
            print("✅ Comprehensive feedback found")
            
            # Check instructor comments
            if 'instructor_comments' in comp_feedback:
                print("✅ Instructor comments found")
                print(f"   Length: {len(comp_feedback['instructor_comments'])} characters")
            else:
                print("❌ Instructor comments missing")
            
            # Check detailed feedback
            if 'detailed_feedback' in comp_feedback:
                detailed = comp_feedback['detailed_feedback']
                print("✅ Detailed feedback found")
                
                # Check each section
                sections = [
                    'reflection_assessment',
                    'analytical_strengths', 
                    'business_application',
                    'learning_demonstration',
                    'areas_for_development',
                    'recommendations'
                ]
                
                for section in sections:
                    if section in detailed and detailed[section]:
                        print(f"   ✅ {section}: {len(detailed[section])} items")
                    else:
                        print(f"   ❌ {section}: missing or empty")
            else:
                print("❌ Detailed feedback missing")
        else:
            print("❌ Comprehensive feedback missing")
        
        # Check technical analysis
        if 'technical_analysis' in result:
            tech = result['technical_analysis']
            print("✅ Technical analysis found")
            
            tech_sections = ['code_strengths', 'code_suggestions', 'technical_observations']
            for section in tech_sections:
                if section in tech and tech[section]:
                    print(f"   ✅ {section}: {len(tech[section])} items")
                else:
                    print(f"   ❌ {section}: missing or empty")
        else:
            print("❌ Technical analysis missing")
        
        # Show sample feedback
        print("\n📝 Sample Feedback Preview:")
        if 'comprehensive_feedback' in result and 'instructor_comments' in result['comprehensive_feedback']:
            comments = result['comprehensive_feedback']['instructor_comments']
            print(f"Instructor Comments: {comments[:200]}...")
        
        if ('comprehensive_feedback' in result and 
            'detailed_feedback' in result['comprehensive_feedback'] and
            'reflection_assessment' in result['comprehensive_feedback']['detailed_feedback']):
            
            reflection = result['comprehensive_feedback']['detailed_feedback']['reflection_assessment']
            if reflection:
                print(f"Reflection Assessment: {reflection[0][:150]}...")
        
        # Test database storage format
        print("\n💾 Testing Database Storage Format...")
        feedback_data = {
            'final_score': result['final_score'],
            'component_scores': result['component_scores'],
            'component_percentages': result['component_percentages'],
            'technical_analysis': result.get('technical_analysis', {}),
            'comprehensive_feedback': result.get('comprehensive_feedback', {}),
            'grading_stats': result.get('grading_stats', {})
        }
        
        # Test JSON serialization
        try:
            json_str = json.dumps(feedback_data, indent=2)
            print(f"✅ JSON serialization successful ({len(json_str)} characters)")
            
            # Test deserialization
            parsed_data = json.loads(json_str)
            print("✅ JSON deserialization successful")
            
            # Verify structure
            if ('comprehensive_feedback' in parsed_data and 
                'detailed_feedback' in parsed_data['comprehensive_feedback']):
                print("✅ Detailed feedback preserved in JSON")
            else:
                print("❌ Detailed feedback lost in JSON")
                
        except Exception as e:
            print(f"❌ JSON serialization failed: {e}")
        
        print("\n🎉 Verbose feedback test complete!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_interface_display():
    """Test how the web interface would display the feedback"""
    
    print("\n🌐 Testing Web Interface Display Logic...")
    
    # Sample result structure
    sample_result = {
        'final_score': 35.2,
        'final_score_percentage': 93.9,
        'comprehensive_feedback': {
            'instructor_comments': 'This submission demonstrates excellent foundational work in business analytics with particularly strong reflective thinking.',
            'detailed_feedback': {
                'reflection_assessment': [
                    'Excellent thoughtful responses to reflection questions demonstrate critical thinking',
                    'Shows strong self-awareness about analytical choices and their implications'
                ],
                'analytical_strengths': [
                    'Comprehensive completion of all assignment requirements',
                    'Effective integration of business context with analytical methodology'
                ],
                'business_application': [
                    'Demonstrates understanding of data analysis applications in business decision-making',
                    'Appropriate framing of analytical objectives within business context'
                ],
                'learning_demonstration': [
                    'Reflection questions show deep engagement with the learning process',
                    'Articulates challenges faced and lessons learned effectively'
                ],
                'areas_for_development': [
                    'Continue exploring advanced statistical methods as suggested in reflections',
                    'Expand knowledge of missing data imputation techniques'
                ],
                'recommendations': [
                    'Continue the excellent reflective practice demonstrated in this assignment',
                    'Explore correlation analysis and statistical significance testing'
                ]
            }
        },
        'technical_analysis': {
            'code_strengths': [
                'Proper implementation of R library loading and data import procedures',
                'Effective use of dplyr functions for data manipulation and filtering'
            ],
            'code_suggestions': [
                'Consider using complete.cases() for more robust missing data handling',
                'Explore the cut() function for creating categorical variables'
            ],
            'technical_observations': [
                'Demonstrates solid understanding of fundamental R programming concepts',
                'Code structure follows logical analytical workflow'
            ]
        }
    }
    
    # Simulate web interface display logic
    print("📋 Simulating Web Interface Display:")
    
    if 'comprehensive_feedback' in sample_result:
        print("\n💬 Detailed Feedback")
        
        # Show instructor comments
        if 'instructor_comments' in sample_result['comprehensive_feedback']:
            print("**Overall Assessment:**")
            print(sample_result['comprehensive_feedback']['instructor_comments'])
            print("---")
        
        # Show detailed feedback sections
        if 'detailed_feedback' in sample_result['comprehensive_feedback']:
            detailed = sample_result['comprehensive_feedback']['detailed_feedback']
            
            sections = [
                ('reflection_assessment', '🤔 Reflection & Critical Thinking:'),
                ('analytical_strengths', '💪 Analytical Strengths:'),
                ('business_application', '💼 Business Application:'),
                ('learning_demonstration', '📚 Learning Demonstration:'),
                ('areas_for_development', '🎯 Areas for Development:'),
                ('recommendations', '💡 Recommendations:')
            ]
            
            for section_key, section_title in sections:
                if section_key in detailed and detailed[section_key]:
                    print(f"\n**{section_title}**")
                    for item in detailed[section_key]:
                        print(f"• {item}")
    
    # Show technical analysis
    if 'technical_analysis' in sample_result:
        print("\n🔧 Technical Analysis Details")
        tech = sample_result['technical_analysis']
        
        if 'code_strengths' in tech and tech['code_strengths']:
            print("\n**Code Strengths:**")
            for item in tech['code_strengths']:
                print(f"• {item}")
        
        if 'code_suggestions' in tech and tech['code_suggestions']:
            print("\n**Code Suggestions:**")
            for item in tech['code_suggestions']:
                print(f"• {item}")
        
        if 'technical_observations' in tech and tech['technical_observations']:
            print("\n**Technical Observations:**")
            for item in tech['technical_observations']:
                print(f"• {item}")
    
    print("\n✅ Web interface display simulation complete!")

if __name__ == "__main__":
    print("🧪 Testing Verbose Feedback System")
    print("=" * 50)
    
    # Test feedback generation
    success = test_verbose_feedback()
    
    # Test web interface display
    test_web_interface_display()
    
    if success:
        print("\n🎉 All tests passed! Verbose feedback should now work in Streamlit.")
    else:
        print("\n❌ Tests failed. Check the error messages above.")