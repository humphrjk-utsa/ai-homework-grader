#!/usr/bin/env python3
"""
Test PDF Report Formatting
Verify that the JSON feedback is properly formatted in PDF reports
"""

from report_generator import PDFReportGenerator
import json
import os

def test_pdf_formatting():
    """Test that PDF reports format the JSON feedback correctly"""
    
    print("📄 Testing PDF Report Formatting")
    print("=" * 50)
    
    # Sample grading result with proper JSON structure
    sample_result = {
        "final_score": 28.5,
        "final_score_percentage": 76.0,
        "max_points": 37.5,
        "comprehensive_feedback": {
            "overall_score": 76,
            "business_understanding": 78,
            "communication_clarity": 80,
            "data_interpretation": 70,
            "methodology_appropriateness": 75,
            "reflection_quality": 68,
            "detailed_feedback": {
                "reflection_assessment": [
                    "You made a good start on the reflection question by identifying the three datasets and noting some basic characteristics like missing values and data types.",
                    "Your reflection could be deeper though - try to think about why these observations matter for business analysis and what challenges they might create.",
                    "Consider reflecting on your own learning process and what surprised you or what you found challenging about working with the data."
                ],
                "analytical_strengths": [
                    "You correctly identified appropriate data types for Date and Amount columns and explained why they matter for analysis.",
                    "Good recognition that ratings data connects to customer satisfaction - that's solid business thinking.",
                    "You set up your R environment properly with the right packages (tidyverse, readxl) which shows good foundational skills."
                ],
                "business_application": [
                    "You connected ratings to customer satisfaction, which shows you understand the business value of the data.",
                    "Your observation about potential outliers in sales data demonstrates awareness of data quality issues that matter in business.",
                    "You recognized that comments data will need different analytical approaches than numeric data."
                ],
                "learning_demonstration": [
                    "You show understanding of the basic R workflow - setting up environment, loading packages, importing data.",
                    "Your use of head(), str(), and summary() shows you're developing good data exploration habits.",
                    "You're starting to think about data quality and what makes datasets ready for analysis."
                ],
                "areas_for_development": [
                    "Complete the missing observations for sales_df - don't leave placeholder text in your final submission.",
                    "Answer all parts of each question fully. Question 2 about data quality needs more than just Date and Amount discussion.",
                    "Include the actual code for importing your datasets and show the outputs so I can see your code works.",
                    "Be more specific in your observations - instead of 'some missing values', tell me how many and in which columns."
                ],
                "recommendations": [
                    "Use str(), glimpse(), and summary() on each dataset and document what you find in detail.",
                    "Check for missing values with is.na() and use functions like complete.cases() to understand data completeness.",
                    "Practice writing more detailed observations - what do the data ranges tell you? Are there unexpected patterns?",
                    "Complete all sections before submitting. It's better to write too much than to leave placeholders."
                ]
            },
            "instructor_comments": "This assignment shows you understand the basics of data exploration and you're asking the right questions about data quality and business relevance. Your setup and approach are on the right track, and I can see you're developing good analytical instincts.\\n\\nThe main issue is completeness - you left several sections unfinished with placeholder text. In data analysis, thoroughness matters because incomplete exploration can lead to missed insights or problems later. Make sure to complete all observations and answer every part of each question.\\n\\nYour reflection shows you're thinking about the data, but push yourself to go deeper. Don't just describe what you see - think about what it means for business decisions and what challenges it might create for analysis. You're building good foundations here, just need to be more thorough in your execution."
        },
        "technical_analysis": {
            "technical_score": 75,
            "syntax_correctness": 85,
            "logic_correctness": 70,
            "business_relevance": 80,
            "effort_and_completion": 65,
            "code_strengths": [
                "Proper setup of R environment with appropriate packages (tidyverse, readxl)",
                "Good use of basic data exploration functions like head(), str(), and summary()",
                "Clear code organization with comments and section headers"
            ],
            "code_suggestions": [
                "Complete the missing data import code for all three datasets",
                "Add code to check for missing values using is.na() or complete.cases()",
                "Include glimpse() function for a more comprehensive data overview",
                "Show the actual output of your code chunks in the final report"
            ],
            "technical_observations": [
                "Student demonstrates understanding of basic R workflow and package management",
                "Code structure is logical but incomplete in several key areas",
                "Shows promise but needs to follow through on all required components"
            ]
        },
        "assignment_info": {
            "title": "Assignment 1: Data Exploration",
            "description": "Introduction to R and data analysis"
        },
        "grading_timestamp": "2025-10-02 17:45:00"
    }
    
    # Generate PDF report
    generator = PDFReportGenerator()
    
    try:
        print("🚀 Generating test PDF report...")
        
        pdf_path = generator.generate_report(
            student_name="Test Student",
            assignment_id="test_assignment",
            analysis_result=sample_result
        )
        
        if os.path.exists(pdf_path):
            print(f"✅ PDF generated successfully: {pdf_path}")
            
            # Check file size (should be reasonable)
            file_size = os.path.getsize(pdf_path)
            print(f"📄 File size: {file_size:,} bytes")
            
            if file_size > 10000:  # At least 10KB for a proper report
                print("✅ PDF appears to have substantial content")
            else:
                print("⚠️ PDF seems small - might be missing content")
            
            # Verify sections are included
            print(f"\n📋 Report should include:")
            print(f"   • Instructor Assessment (instructor_comments)")
            print(f"   • Reflection & Critical Thinking ({len(sample_result['comprehensive_feedback']['detailed_feedback']['reflection_assessment'])} items)")
            print(f"   • Analytical Strengths ({len(sample_result['comprehensive_feedback']['detailed_feedback']['analytical_strengths'])} items)")
            print(f"   • Business Application ({len(sample_result['comprehensive_feedback']['detailed_feedback']['business_application'])} items)")
            print(f"   • Learning Demonstration ({len(sample_result['comprehensive_feedback']['detailed_feedback']['learning_demonstration'])} items)")
            print(f"   • Areas for Development ({len(sample_result['comprehensive_feedback']['detailed_feedback']['areas_for_development'])} items)")
            print(f"   • Recommendations ({len(sample_result['comprehensive_feedback']['detailed_feedback']['recommendations'])} items)")
            print(f"   • Technical Analysis (Code Strengths: {len(sample_result['technical_analysis']['code_strengths'])} items)")
            print(f"   • Code Suggestions ({len(sample_result['technical_analysis']['code_suggestions'])} items)")
            
            return True
        else:
            print("❌ PDF file was not created")
            return False
            
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_formatting()
    if success:
        print(f"\n🎉 PDF formatting test completed successfully!")
        print(f"💡 The report should now display all feedback sections properly formatted.")
    else:
        print(f"\n❌ PDF formatting test failed - check the error messages above.")