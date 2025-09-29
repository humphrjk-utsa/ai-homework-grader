#!/usr/bin/env python3
"""
Test PDF report generation with verbose feedback from Business Analytics Grader
"""

import json
import os
from report_generator import PDFReportGenerator
from business_analytics_grader import BusinessAnalyticsGrader

def test_pdf_with_verbose_feedback():
    """Test PDF generation with comprehensive feedback"""
    
    print("📄 Testing PDF Report with Verbose Feedback...")
    
    # Sample comprehensive result from Business Analytics Grader
    sample_result = {
        'final_score': 34.5,
        'final_score_percentage': 92.1,
        'max_points': 37.5,
        'component_scores': {
            'technical_points': 8.8,
            'business_points': 10.4,
            'analysis_points': 8.6,
            'communication_points': 6.7,
            'bonus_points': 0.0
        },
        'comprehensive_feedback': {
            'instructor_comments': 'This submission demonstrates excellent foundational work in business analytics with particularly strong reflective thinking. Your thoughtful responses to the reflection questions show genuine engagement with the learning process and critical thinking about your analytical choices. The systematic approach to data exploration, integration of business context, and honest assessment of limitations are all commendable. Your reflections demonstrate a growth mindset and understanding that will serve you well in future analytical work.',
            'detailed_feedback': {
                'reflection_assessment': [
                    'Excellent thoughtful responses to reflection questions demonstrate critical thinking',
                    'Shows strong self-awareness about analytical choices and their implications',
                    'Demonstrates understanding of limitations and areas for improvement',
                    'Evidence of genuine learning and growth mindset throughout the assignment'
                ],
                'analytical_strengths': [
                    'Comprehensive completion of all assignment requirements',
                    'Effective integration of business context with analytical methodology',
                    'Clear and systematic presentation of analytical findings',
                    'Appropriate use of statistical measures and data visualization techniques'
                ],
                'business_application': [
                    'Demonstrates understanding of data analysis applications in business decision-making',
                    'Appropriate framing of analytical objectives within business context',
                    'Recognition of practical implications for organizational strategy'
                ],
                'learning_demonstration': [
                    'Reflection questions show deep engagement with the learning process',
                    'Articulates challenges faced and lessons learned effectively',
                    'Shows understanding of the iterative nature of data analysis',
                    'Demonstrates awareness of ethical considerations in data handling'
                ],
                'areas_for_development': [
                    'Continue exploring advanced statistical methods as suggested in reflections',
                    'Expand knowledge of missing data imputation techniques',
                    'Develop skills in causal inference and experimental design'
                ],
                'recommendations': [
                    'Continue the excellent reflective practice demonstrated in this assignment',
                    'Explore correlation analysis and statistical significance testing',
                    'Practice with larger, more complex datasets to build analytical confidence',
                    'Consider taking additional courses in advanced statistical methods'
                ]
            }
        },
        'technical_analysis': {
            'technical_score': 94,
            'syntax_correctness': 96,
            'logic_correctness': 92,
            'business_relevance': 94,
            'effort_and_completion': 96,
            'code_strengths': [
                'Proper implementation of R library loading and data import procedures',
                'Effective use of dplyr functions for data manipulation and filtering',
                'Appropriate application of ggplot2 for data visualization',
                'Systematic approach to data exploration and summary statistics',
                'Complete execution of all required analytical components'
            ],
            'code_suggestions': [
                'Consider using complete.cases() for more robust missing data handling',
                'Explore the cut() function for creating categorical variables from continuous data',
                'Add correlation analysis using cor() to quantify relationships between variables',
                'Include additional summary statistics such as standard deviation and quartiles'
            ],
            'technical_observations': [
                'Demonstrates solid understanding of fundamental R programming concepts',
                'Code structure follows logical analytical workflow',
                'Shows appropriate selection of analytical tools for the business context',
                'Evidence of careful attention to data quality and integrity'
            ]
        },
        'grading_method': 'business_analytics_system',
        'grading_timestamp': '2024-01-15 14:30:22',
        'parallel_processing': True
    }
    
    # Convert to format expected by PDF generator
    analysis_result = {
        'total_score': sample_result['final_score'],
        'max_score': 37.5,
        'element_scores': {
            'technical_execution': sample_result['component_scores']['technical_points'],
            'business_thinking': sample_result['component_scores']['business_points'],
            'data_analysis': sample_result['component_scores']['analysis_points'],
            'communication': sample_result['component_scores']['communication_points']
        },
        # Include comprehensive feedback
        'comprehensive_feedback': sample_result['comprehensive_feedback'],
        # Include technical analysis
        'technical_analysis': sample_result['technical_analysis'],
        # Add metadata
        'grading_method': sample_result['grading_method'],
        'grading_timestamp': sample_result['grading_timestamp'],
        'parallel_processing': sample_result['parallel_processing']
    }
    
    try:
        # Generate PDF report
        report_generator = PDFReportGenerator()
        pdf_path = report_generator.generate_report(
            student_name="Test Student",
            assignment_id="Assignment 1 - Introduction to R",
            analysis_result=analysis_result
        )
        
        print(f"✅ PDF report generated successfully: {pdf_path}")
        
        # Check file exists and has content
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"📊 PDF file size: {file_size:,} bytes")
            
            if file_size > 10000:  # At least 10KB
                print("✅ PDF appears to have substantial content")
            else:
                print("⚠️ PDF file seems small - may be missing content")
        else:
            print("❌ PDF file not found")
            return False
        
        # Verify sections are included
        print("\n📋 Verifying PDF Content Structure:")
        
        # Check that comprehensive feedback sections would be included
        comp_feedback = analysis_result.get('comprehensive_feedback', {})
        if 'detailed_feedback' in comp_feedback:
            detailed = comp_feedback['detailed_feedback']
            
            sections = [
                ('reflection_assessment', 'Reflection & Critical Thinking'),
                ('analytical_strengths', 'Analytical Strengths'),
                ('business_application', 'Business Application'),
                ('learning_demonstration', 'Learning Demonstration'),
                ('areas_for_development', 'Areas for Development'),
                ('recommendations', 'Recommendations')
            ]
            
            for section_key, section_title in sections:
                if section_key in detailed and detailed[section_key]:
                    item_count = len(detailed[section_key])
                    print(f"   ✅ {section_title}: {item_count} items")
                else:
                    print(f"   ❌ {section_title}: missing")
        
        # Check technical analysis
        tech_analysis = analysis_result.get('technical_analysis', {})
        tech_sections = [
            ('code_strengths', 'Code Strengths'),
            ('code_suggestions', 'Code Suggestions'),
            ('technical_observations', 'Technical Observations')
        ]
        
        for section_key, section_title in tech_sections:
            if section_key in tech_analysis and tech_analysis[section_key]:
                item_count = len(tech_analysis[section_key])
                print(f"   ✅ {section_title}: {item_count} items")
            else:
                print(f"   ❌ {section_title}: missing")
        
        print(f"\n🎉 PDF test complete! Open the file to verify content:")
        print(f"   {pdf_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pdf_with_real_grading():
    """Test PDF generation with actual Business Analytics Grader output"""
    
    print("\n🤖 Testing PDF with Real Business Analytics Grader...")
    
    try:
        # Initialize grader
        grader = BusinessAnalyticsGrader()
        
        # Sample student work
        student_code = '''
library(tidyverse)
library(readxl)

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

## Reflection Questions

[What challenges did you encounter?]
The main challenge was understanding the Excel file structure with multiple sheets.

[What did you learn?]
I learned how to import different file types and perform basic data exploration.

[How is this useful for business?]
This analysis helps understand sales patterns and customer satisfaction.
'''
        
        solution_code = '''
library(tidyverse)
library(readxl)

sales_df <- read_csv("data/sales_data.csv")
ratings_df <- read_excel("data/customer_feedback.xlsx", sheet = "ratings")
'''
        
        assignment_info = {
            "title": "Assignment 1 - Introduction to R",
            "student_name": "Real Test Student"
        }
        
        rubric_elements = {
            "technical_execution": {"weight": 0.25, "max_score": 37.5},
            "business_thinking": {"weight": 0.30, "max_score": 37.5},
            "data_analysis": {"weight": 0.25, "max_score": 37.5},
            "communication": {"weight": 0.20, "max_score": 37.5}
        }
        
        # Grade the submission
        print("⚡ Grading with Business Analytics AI...")
        result = grader.grade_submission(
            student_code=student_code,
            student_markdown=student_markdown,
            solution_code=solution_code,
            assignment_info=assignment_info,
            rubric_elements=rubric_elements
        )
        
        print(f"✅ Grading complete! Score: {result['final_score']}/37.5")
        
        # Convert to PDF format
        analysis_result = {
            'total_score': result['final_score'],
            'max_score': 37.5,
            'element_scores': {
                'technical_execution': result['component_scores']['technical_points'],
                'business_thinking': result['component_scores']['business_points'],
                'data_analysis': result['component_scores']['analysis_points'],
                'communication': result['component_scores']['communication_points']
            },
            'comprehensive_feedback': result.get('comprehensive_feedback', {}),
            'technical_analysis': result.get('technical_analysis', {}),
            'grading_method': result.get('grading_method', 'business_analytics_system'),
            'grading_timestamp': result.get('grading_timestamp', ''),
            'parallel_processing': result.get('parallel_processing', False)
        }
        
        # Generate PDF
        report_generator = PDFReportGenerator()
        pdf_path = report_generator.generate_report(
            student_name="Real_Test_Student",
            assignment_id="Assignment 1 - Introduction to R",
            analysis_result=analysis_result
        )
        
        print(f"✅ Real grading PDF generated: {pdf_path}")
        
        # Check file size
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"📊 PDF file size: {file_size:,} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Real grading PDF test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run PDF verbose feedback tests"""
    
    print("📄 Testing PDF Reports with Verbose Feedback")
    print("=" * 60)
    
    # Test with sample data
    test1_success = test_pdf_with_verbose_feedback()
    
    # Test with real grading
    test2_success = test_pdf_with_real_grading()
    
    print("\n📊 Test Summary:")
    print(f"   Sample data PDF: {'✅' if test1_success else '❌'}")
    print(f"   Real grading PDF: {'✅' if test2_success else '❌'}")
    
    if test1_success and test2_success:
        print("\n🎉 All PDF tests passed!")
        print("📋 The PDF reports now include comprehensive verbose feedback from the Business Analytics Grader")
        print("📁 Check the 'reports' folder for generated PDF files")
    else:
        print("\n⚠️ Some PDF tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()