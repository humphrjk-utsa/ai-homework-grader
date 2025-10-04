#!/usr/bin/env python3
"""
Test JSON Parsing in Report Generation
Verify that structured responses are properly parsed
"""

from business_analytics_grader import BusinessAnalyticsGrader
import json

def test_json_parsing():
    """Test that JSON responses are properly parsed"""
    
    print("🧪 Testing JSON Parsing in Report Generation")
    print("=" * 50)
    
    grader = BusinessAnalyticsGrader()
    
    # Test code analysis parsing
    sample_code_response = '''
Here is my analysis of the R code:

```json
{
    "technical_score": 95,
    "syntax_correctness": 98,
    "logic_correctness": 92,
    "business_relevance": 94,
    "effort_and_completion": 96,
    "code_strengths": [
        "Excellent use of dplyr for data manipulation",
        "Proper implementation of ggplot2 for visualization",
        "Good data cleaning practices with filter operations",
        "Effective use of case_when for categorization"
    ],
    "code_suggestions": [
        "Consider adding correlation analysis using cor()",
        "Include additional summary statistics like standard deviation",
        "Add error handling for file reading operations"
    ],
    "technical_observations": [
        "Code follows logical analytical workflow",
        "Demonstrates solid understanding of R programming concepts",
        "Shows appropriate selection of analytical tools"
    ]
}
```

The student has demonstrated strong technical skills.
'''
    
    # Test feedback parsing
    sample_feedback_response = '''
Based on my evaluation of this business analytics assignment:

```json
{
    "overall_score": 94,
    "business_understanding": 92,
    "communication_clarity": 90,
    "data_interpretation": 93,
    "methodology_appropriateness": 91,
    "reflection_quality": 95,
    "detailed_feedback": {
        "reflection_assessment": [
            "Excellent thoughtful responses to reflection questions demonstrate critical thinking",
            "Shows strong self-awareness about analytical choices and their implications",
            "Demonstrates understanding of limitations and areas for improvement"
        ],
        "analytical_strengths": [
            "Comprehensive completion of all assignment requirements",
            "Effective integration of business context with analytical methodology",
            "Clear and systematic presentation of analytical findings"
        ],
        "business_application": [
            "Demonstrates understanding of data analysis applications in business decision-making",
            "Appropriate framing of analytical objectives within business context"
        ],
        "learning_demonstration": [
            "Reflection questions show deep engagement with the learning process",
            "Articulates challenges faced and lessons learned effectively"
        ],
        "areas_for_development": [
            "Continue exploring advanced statistical methods",
            "Expand knowledge of missing data imputation techniques"
        ],
        "recommendations": [
            "Continue the excellent reflective practice demonstrated",
            "Explore correlation analysis and statistical significance testing"
        ]
    },
    "instructor_comments": "This submission demonstrates excellent foundational work in business analytics with particularly strong reflective thinking. Your thoughtful responses to the reflection questions show genuine engagement with the learning process and critical thinking about your analytical choices. The systematic approach to data exploration, integration of business context, and honest assessment of limitations are all commendable. Your reflections demonstrate a growth mindset and understanding that will serve you well in future analytical work. Continue this level of thoughtful engagement with your learning."
}
```

This is a strong submission overall.
'''
    
    print("🔧 Testing Code Analysis Parsing...")
    code_result = grader._parse_code_analysis_response(sample_code_response)
    
    print(f"✅ Technical Score: {code_result.get('technical_score')}")
    print(f"✅ Code Strengths Count: {len(code_result.get('code_strengths', []))}")
    print(f"✅ Code Suggestions Count: {len(code_result.get('code_suggestions', []))}")
    
    if code_result.get('technical_score') == 95:
        print("✅ PASS: Code analysis JSON parsing works correctly")
    else:
        print("❌ FAIL: Code analysis JSON parsing failed")
    
    print(f"\n📝 Testing Feedback Parsing...")
    feedback_result = grader._parse_feedback_response(sample_feedback_response)
    
    print(f"✅ Overall Score: {feedback_result.get('overall_score')}")
    print(f"✅ Reflection Quality: {feedback_result.get('reflection_quality')}")
    
    detailed_feedback = feedback_result.get('detailed_feedback', {})
    reflection_assessment = detailed_feedback.get('reflection_assessment', [])
    print(f"✅ Reflection Assessment Items: {len(reflection_assessment)}")
    
    instructor_comments = feedback_result.get('instructor_comments', '')
    print(f"✅ Instructor Comments Length: {len(instructor_comments)} characters")
    
    if (feedback_result.get('overall_score') == 94 and 
        len(reflection_assessment) == 3 and 
        len(instructor_comments) > 500):
        print("✅ PASS: Feedback JSON parsing works correctly")
    else:
        print("❌ FAIL: Feedback JSON parsing failed")
    
    # Test plain text fallback
    print(f"\n🔄 Testing Plain Text Fallback...")
    plain_text_response = """
    This is a good submission. The student shows strong analytical skills and business understanding.
    The code is well-structured and the analysis is thorough. Areas for improvement include adding
    more statistical tests and expanding the business implications section.
    """
    
    fallback_result = grader._parse_feedback_response(plain_text_response)
    fallback_comments = fallback_result.get('instructor_comments', '')
    
    if len(fallback_comments) > 100:
        print("✅ PASS: Plain text fallback preserves full content")
    else:
        print("❌ FAIL: Plain text fallback truncates content")
    
    print(f"\n🎉 JSON Parsing Test Complete!")

if __name__ == "__main__":
    test_json_parsing()