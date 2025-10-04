#!/usr/bin/env python3
"""
Test Clean Report Content
Verify that all internal AI monologue is removed from reports
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add current directory to path
sys.path.append('.')

from report_generator import PDFReportGenerator

def create_dirty_ai_response():
    """Create AI response with internal monologue that should be filtered out"""
    
    dirty_response = """
Instructor Assessment We need to evaluate the student's actual work. Let's read the submission. The student provided a written assignment with sections. They have code for data import, initial assessment, missing value analysis, removal, imputation, outlier detection, capping, final dataset, comparison summary. They also answered reflection questions in text. We need to assess based on actual work. First, check completeness: Did they complete all required parts? The assignment required Part 1: import and assessment. They did import, printed structure, summary, and wrote observations. Good. Part 2: missing value analysis and treatment. They computed total missing, missing per column, removed rows, imputed Customer_Name with mode, imputed Quantity with median, imputed Sales_Amount with median (though they used median for Sales_Amount, but they also discuss not imputing). They also compared summary stats after removal and imputation. So they completed. Part 3: outlier detection and treatment. They computed IQR thresholds, flagged outliers, created boxplot, removed outliers using Z-score >3, also performed capping (winsorization) for numeric columns, then specifically capped Sales_Amount. They printed summary, final dataset. Part 4: final dataset justification: they wrote justification in the markdown earlier (selected sales_outliers_capped). They also created comparison summary table. Part 5: reflection questions: They answered Q1 (missing value strategy), Q2 (outlier interpretation), Q3 (data quality impact), Q4 (ethical considerations). They gave thorough answers. Thus they completed all parts. Now evaluate quality. Reflection quality: They gave detailed answers, with bullet points, examples, trade-offs, business impact, ethical considerations. Good depth. Business understanding: They discuss business implications of missing values, outliers, forecasting, etc. Good. Communication clarity: The writing is fairly clear, though some formatting issues (some stray markdown). But overall understandable. Data interpretation: They identified missing values, outliers, gave counts, described issues. They used code to compute missing counts, outlier counts, etc. They gave some analysis of impact. Methodology appropriateness: They used appropriate methods: removal, mode/median imputation, IQR for outliers, winsorization. They also used Z-score removal. They could have discussed why choose median for Sales_Amount (they earlier said not to impute). But they still imputed median for Sales_Amount. Slight inconsistency. But overall appropriate. Reflection quality: Good. Now assign scores. Overall score: maybe 88. Business understanding: 92. Communication clarity: 85. Data interpretation: 88. Methodology appropriateness: 84. Reflection quality: 90. Now produce detailed feedback. We need to list bullet points under each category. Now produce JSON. Let's craft feedback.

{
  "overall_score": 88,
  "business_understanding": 92,
  "communication_clarity": 85,
  "data_interpretation": 88,
  "methodology_appropriateness": 84,
  "reflection_quality": 90,
  "detailed_feedback": {
    "reflection_assessment": [
      "Your reflection answers are thorough and well-structured. You clearly differentiate when removal versus imputation is appropriate.",
      "The discussion of outlier interpretation and ethical considerations shows a solid grasp of the broader impact of data-cleaning decisions.",
      "A deeper dive into the potential bias introduced by median imputation would strengthen the reflection."
    ],
    "analytical_strengths": [
      "You successfully imported the dataset, inspected its structure, and produced a concise summary of missingness.",
      "The mode function you wrote for categorical imputation works correctly, demonstrating practical handling of different data types.",
      "Outlier detection using the IQR rule, Z-score filtering, and winsorization are all correctly implemented."
    ],
    "business_application": [
      "You linked each cleaning step to a business outcome – preserving sample size for forecasting, avoiding bias in revenue totals.",
      "Your justification for choosing the capped dataset references real-world concerns about legitimate sales spikes.",
      "The ethical section highlights reproducibility, bias amplification, and governance awareness."
    ],
    "learning_demonstration": [
      "Your work demonstrates competency with R functions and data manipulation techniques.",
      "You show understanding of when to apply different imputation and outlier treatment methods.",
      "The comparison table effectively quantifies the impact of your cleaning decisions."
    ],
    "areas_for_development": [
      "Consider documenting your decision-making process more explicitly in future assignments.",
      "Work on consistency between your stated approach and actual implementation.",
      "Focus on providing more detailed justification for methodological choices."
    ],
    "recommendations": [
      "Practice with more complex datasets to strengthen your analytical skills.",
      "Explore advanced imputation techniques for future projects.",
      "Develop stronger documentation habits for reproducible analysis."
    ]
  },
  "instructor_comments": "Your work demonstrates solid analytical thinking and technical execution. You've successfully completed all required components and shown good understanding of data cleaning principles. The reflection questions reveal thoughtful consideration of business implications and ethical considerations. Continue to focus on consistency between your stated methodology and implementation, and work on developing more detailed documentation practices."
}
"""
    
    return dirty_response

def create_test_data():
    """Create test data with dirty AI responses"""
    
    return {
        'student_name': 'Test Student',
        'assignment_name': 'Data Cleaning Assignment',
        'submission_date': '2024-01-15',
        'overall_score': 88,
        'max_score': 100,
        'comprehensive_feedback': create_dirty_ai_response(),
        'question_feedback': [
            {
                'question': 'Q1: Missing Value Strategy',
                'score': 22,
                'max_score': 25,
                'detailed_feedback': create_dirty_ai_response()
            },
            {
                'question': 'Q2: Outlier Interpretation', 
                'score': 23,
                'max_score': 25,
                'detailed_feedback': create_dirty_ai_response()
            }
        ]
    }

def test_clean_report_generation():
    """Test that reports are generated without internal AI monologue"""
    
    print("Testing clean report generation...")
    
    # Create test data with dirty AI responses
    test_data = create_test_data()
    
    # Create temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate report with correct parameters
        generator = PDFReportGenerator(temp_dir)
        output_path = generator.generate_report(
            student_name=test_data['student_name'],
            assignment_id=test_data['assignment_name'], 
            analysis_result=test_data
        )
        
        # Verify file was created
        assert os.path.exists(output_path), "Report file was not created"
        
        print(f"✓ Report generated successfully at {output_path}")
        print(f"✓ File size: {os.path.getsize(output_path)} bytes")
        
        return True

def test_json_extraction():
    """Test that JSON extraction works correctly"""
    
    print("\nTesting JSON extraction...")
    
    generator = PDFReportGenerator()
    dirty_response = create_dirty_ai_response()
    
    # Test JSON extraction
    extracted_json = generator._extract_json_from_response(dirty_response)
    
    assert extracted_json is not None, "Failed to extract JSON from response"
    assert 'instructor_comments' in extracted_json, "Missing instructor_comments in extracted JSON"
    assert 'detailed_feedback' in extracted_json, "Missing detailed_feedback in extracted JSON"
    
    print("✓ JSON extraction successful")
    print(f"✓ Extracted keys: {list(extracted_json.keys())}")
    
    # Test instructor comments cleaning
    raw_comments = extracted_json['instructor_comments']
    clean_comments = generator._clean_instructor_comments(raw_comments)
    
    print(f"✓ Raw comments length: {len(raw_comments)}")
    print(f"✓ Clean comments length: {len(clean_comments)}")
    print(f"✓ Clean comments: {clean_comments[:100]}...")
    
    # Verify no internal AI patterns remain
    forbidden_patterns = [
        "we need to", "let's", "first, check", "now evaluate", "now assign",
        "the student provided", "they have code", "good.", "thus they"
    ]
    
    for pattern in forbidden_patterns:
        assert pattern not in clean_comments.lower(), f"Found forbidden pattern '{pattern}' in clean comments"
    
    print("✓ No forbidden AI patterns found in clean comments")
    
    return True

def test_feedback_filtering():
    """Test that feedback filtering removes internal AI reasoning"""
    
    print("\nTesting feedback filtering...")
    
    generator = PDFReportGenerator()
    dirty_response = create_dirty_ai_response()
    
    # Test filtering
    clean_feedback = generator._filter_instructor_feedback(dirty_response)
    
    print(f"✓ Original length: {len(dirty_response)}")
    print(f"✓ Filtered length: {len(clean_feedback)}")
    print(f"✓ Filtered content: {clean_feedback[:200]}...")
    
    # Verify no internal reasoning remains
    forbidden_patterns = [
        "we need to evaluate", "let's read", "first, check completeness",
        "now evaluate quality", "now assign scores", "now produce json"
    ]
    
    for pattern in forbidden_patterns:
        assert pattern not in clean_feedback.lower(), f"Found forbidden pattern '{pattern}' in filtered feedback"
    
    print("✓ No internal reasoning patterns found in filtered feedback")
    
    return True

def main():
    """Run all tests"""
    
    print("=" * 60)
    print("TESTING CLEAN REPORT CONTENT GENERATION")
    print("=" * 60)
    
    try:
        # Run tests
        test_json_extraction()
        test_feedback_filtering() 
        test_clean_report_generation()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED - Reports are now clean of AI monologue!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)