#!/usr/bin/env python3
"""
Test that the web interface is properly connected to our business analytics grader
"""

import sqlite3
import pandas as pd
import json
import os

def test_database_setup():
    """Test that the database is properly set up"""
    
    db_path = "homework_grader/grading_database.db"
    
    if not os.path.exists(db_path):
        print("❌ Database not found")
        return False
    
    conn = sqlite3.connect(db_path)
    
    try:
        # Test assignments table
        assignments = pd.read_sql_query("SELECT * FROM assignments", conn)
        print(f"✅ Assignments table: {len(assignments)} records")
        
        if len(assignments) > 0:
            assignment = assignments.iloc[0]
            print(f"   • Assignment: {assignment['name']}")
            print(f"   • Total Points: {assignment['total_points']}")
            
            # Check rubric
            if assignment['rubric']:
                try:
                    rubric = json.loads(assignment['rubric'])
                    print(f"   • Rubric loaded: {len(rubric)} elements")
                except:
                    print("   ⚠️ Rubric format issue")
        
        # Test students table
        students = pd.read_sql_query("SELECT * FROM students", conn)
        print(f"✅ Students table: {len(students)} records")
        
        if len(students) > 0:
            student = students.iloc[0]
            print(f"   • Student: {student['name']} ({student['student_id']})")
        
        # Test submissions table
        submissions = pd.read_sql_query("SELECT * FROM submissions", conn)
        print(f"✅ Submissions table: {len(submissions)} records")
        
        if len(submissions) > 0:
            submission = submissions.iloc[0]
            print(f"   • Submission: {submission['notebook_path']}")
            print(f"   • Graded: {'Yes' if submission['ai_score'] else 'No'}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        conn.close()
        return False

def test_grader_connection():
    """Test that our business analytics grader is accessible"""
    
    try:
        from business_analytics_grader import BusinessAnalyticsGrader
        from grading_validator import GradingValidator
        from connect_web_interface import grade_submissions_page
        
        print("✅ Business Analytics Grader imported successfully")
        print("✅ Grading Validator imported successfully")
        print("✅ Web interface connection imported successfully")
        
        # Test grader initialization
        grader = BusinessAnalyticsGrader()
        print("✅ Business Analytics Grader initialized")
        
        # Test validator initialization
        validator = GradingValidator()
        print("✅ Grading Validator initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Grader connection test failed: {e}")
        return False

def test_file_paths():
    """Test that required files exist"""
    
    required_files = [
        "homework_grader/app.py",
        "homework_grader/business_analytics_grader.py",
        "homework_grader/grading_validator.py",
        "homework_grader/connect_web_interface.py",
        "homework_grader/assignment_1_rubric.json",
        "homework_grader/Balfour_Logan_homework_lesson_1.ipynb"
    ]
    
    all_exist = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    
    print("🧪 Testing Web Interface Connection")
    print("=" * 50)
    
    # Test file paths
    print("\n📁 File Path Tests:")
    files_ok = test_file_paths()
    
    # Test database
    print("\n🗄️ Database Tests:")
    db_ok = test_database_setup()
    
    # Test grader connection
    print("\n🤖 Grader Connection Tests:")
    grader_ok = test_grader_connection()
    
    # Final result
    print("\n" + "=" * 50)
    
    if files_ok and db_ok and grader_ok:
        print("🎉 ALL TESTS PASSED!")
        print("\n🚀 Your web interface is ready to use:")
        print("   cd homework_grader")
        print("   streamlit run app.py")
        print("\n📋 What you can do:")
        print("   • Create and manage assignments")
        print("   • Upload student submissions")
        print("   • Grade with Business Analytics AI")
        print("   • Review and correct AI grades")
        print("   • Generate detailed PDF reports")
        print("   • Export results to CSV")
        print("   • Train the AI on your grading style")
    else:
        print("❌ SOME TESTS FAILED")
        print("   Check the errors above and fix them before using the web interface")

if __name__ == "__main__":
    main()