#!/usr/bin/env python3
"""
Test Database Filtering
Verify that AI feedback is filtered BEFORE being stored in the database
"""

import json
import tempfile
import sqlite3
from ai_grader import filter_ai_feedback_for_storage

def create_dirty_feedback():
    """Create feedback with internal AI monologue"""
    return {
        "comprehensive_feedback": """
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
        """,
        "final_score": 88
    }

def test_database_filtering():
    """Test that filtering works at database storage level"""
    
    print("🧪 Testing Database-Level Filtering")
    print("=" * 50)
    
    # Create dirty feedback
    dirty_feedback = create_dirty_feedback()
    
    print(f"📥 Original feedback length: {len(str(dirty_feedback))}")
    print(f"📥 Contains internal monologue: {'We need to evaluate' in str(dirty_feedback)}")
    
    # Apply filtering (simulating what happens before database storage)
    filtered_feedback = filter_ai_feedback_for_storage(dirty_feedback)
    
    print(f"📤 Filtered feedback length: {len(str(filtered_feedback))}")
    print(f"📤 Contains internal monologue: {'We need to evaluate' in str(filtered_feedback)}")
    
    # Test specific patterns that should be removed
    forbidden_patterns = [
        "We need to evaluate",
        "Let's read the submission", 
        "The student provided",
        "They have code",
        "First, check completeness",
        "Now evaluate quality",
        "Now assign scores",
        "Now produce JSON",
        "Let's craft feedback"
    ]
    
    patterns_found = []
    for pattern in forbidden_patterns:
        if pattern in str(filtered_feedback):
            patterns_found.append(pattern)
    
    if patterns_found:
        print(f"❌ Found forbidden patterns: {patterns_found}")
        return False
    else:
        print("✅ No forbidden patterns found in filtered feedback")
    
    # Test that good content is preserved
    if isinstance(filtered_feedback, dict) and 'comprehensive_feedback' in filtered_feedback:
        comp_feedback = filtered_feedback['comprehensive_feedback']
        
        # Check if instructor comments are preserved and clean
        if isinstance(comp_feedback, dict) and 'instructor_comments' in comp_feedback:
            instructor_comments = comp_feedback['instructor_comments']
            print(f"✅ Instructor comments preserved: {len(instructor_comments)} characters")
            print(f"✅ Sample: {instructor_comments[:100]}...")
        
        # Check if detailed feedback sections are preserved
        if isinstance(comp_feedback, dict) and 'detailed_feedback' in comp_feedback:
            detailed = comp_feedback['detailed_feedback']
            print(f"✅ Detailed feedback sections preserved: {list(detailed.keys())}")
            
            # Check that each section has clean content
            for section_name, section_content in detailed.items():
                if isinstance(section_content, list) and section_content:
                    print(f"  - {section_name}: {len(section_content)} items")
                    # Check first item for cleanliness
                    first_item = section_content[0]
                    if any(pattern in first_item.lower() for pattern in ["we need", "let's", "the student"]):
                        print(f"    ❌ Section {section_name} still contains internal reasoning")
                        return False
                    else:
                        print(f"    ✅ Section {section_name} is clean")
    
    print("\n🎉 Database filtering test passed!")
    return True

def test_database_simulation():
    """Simulate storing and retrieving from database with filtering"""
    
    print("\n🧪 Testing Database Storage Simulation")
    print("=" * 50)
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        # Create database and table
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE submissions (
                id INTEGER PRIMARY KEY,
                student_id TEXT,
                ai_feedback TEXT
            )
        """)
        
        # Create dirty feedback
        dirty_feedback = create_dirty_feedback()
        
        # Apply filtering before storage (this is what our fix does)
        filtered_feedback = filter_ai_feedback_for_storage(dirty_feedback)
        
        # Store filtered feedback in database
        cursor.execute("""
            INSERT INTO submissions (student_id, ai_feedback)
            VALUES (?, ?)
        """, ("test_student", json.dumps(filtered_feedback)))
        
        conn.commit()
        
        # Retrieve from database
        cursor.execute("SELECT ai_feedback FROM submissions WHERE student_id = ?", ("test_student",))
        stored_feedback = cursor.fetchone()[0]
        
        # Parse stored feedback
        parsed_feedback = json.loads(stored_feedback)
        
        print(f"✅ Successfully stored and retrieved feedback")
        print(f"✅ Stored feedback length: {len(stored_feedback)}")
        
        # Verify no internal monologue in stored data
        forbidden_patterns = [
            "We need to evaluate",
            "Let's read", 
            "The student provided",
            "Now evaluate",
            "Now assign scores"
        ]
        
        patterns_found = []
        for pattern in forbidden_patterns:
            if pattern in stored_feedback:
                patterns_found.append(pattern)
        
        if patterns_found:
            print(f"❌ Database contains forbidden patterns: {patterns_found}")
            return False
        else:
            print("✅ Database contains no forbidden patterns")
        
        conn.close()
        
        print("🎉 Database simulation test passed!")
        return True
        
    finally:
        # Clean up
        import os
        if os.path.exists(db_path):
            os.unlink(db_path)

def main():
    """Run all database filtering tests"""
    
    print("🔍 DATABASE FILTERING TESTS")
    print("=" * 60)
    
    try:
        # Test filtering function
        test1_passed = test_database_filtering()
        
        # Test database simulation
        test2_passed = test_database_simulation()
        
        if test1_passed and test2_passed:
            print("\n" + "=" * 60)
            print("🎉 ALL DATABASE FILTERING TESTS PASSED!")
            print("✅ AI feedback is now filtered BEFORE database storage")
            print("✅ No internal monologue will be stored in the database")
            print("✅ Reports will be clean from the source")
            print("=" * 60)
            return True
        else:
            print("\n❌ Some tests failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)