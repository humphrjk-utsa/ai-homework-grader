#!/usr/bin/env python3
"""
Test the updated training interface
"""

import sqlite3
import pandas as pd
from training_interface import TrainingInterface

class MockGrader:
    """Mock grader for testing"""
    def __init__(self):
        self.db_path = "grading_database.db"

def test_training_interface():
    """Test that the training interface can find submissions"""
    
    print("🧪 Testing Training Interface...")
    
    # Check if database exists
    import os
    if not os.path.exists("grading_database.db"):
        print("❌ No database found - create some graded submissions first")
        return False
    
    try:
        # Initialize training interface
        mock_grader = MockGrader()
        training_interface = TrainingInterface(mock_grader)
        
        # Test getting submissions for review
        submissions = training_interface.get_submissions_for_review("All Assignments", "All")
        
        print(f"✅ Found {len(submissions)} submissions for review")
        
        if len(submissions) > 0:
            print("📋 Sample submission data:")
            sample = submissions.iloc[0]
            print(f"   Student: {sample['student_name']}")
            print(f"   Assignment: {sample['assignment_name']}")
            print(f"   AI Score: {sample['ai_score']}")
            print(f"   Human Score: {sample.get('human_score', 'Not set')}")
            
            # Test feedback parsing
            if sample['ai_feedback']:
                try:
                    import json
                    feedback_data = json.loads(sample['ai_feedback'])
                    
                    if isinstance(feedback_data, dict) and 'comprehensive_feedback' in feedback_data:
                        print("   ✅ Comprehensive feedback format detected")
                        comp_feedback = feedback_data['comprehensive_feedback']
                        
                        if 'instructor_comments' in comp_feedback:
                            comments_len = len(comp_feedback['instructor_comments'])
                            print(f"   📝 Instructor comments: {comments_len} characters")
                        
                        if 'detailed_feedback' in comp_feedback:
                            detailed = comp_feedback['detailed_feedback']
                            total_items = sum(len(items) if isinstance(items, list) else 0 
                                            for items in detailed.values())
                            print(f"   📊 Detailed feedback items: {total_items}")
                    
                    elif isinstance(feedback_data, list):
                        print(f"   ℹ️ Legacy feedback format: {len(feedback_data)} items")
                    
                    else:
                        print("   ⚠️ Unknown feedback format")
                        
                except:
                    print("   ⚠️ Feedback is not JSON format")
        
        # Test training stats
        conn = sqlite3.connect("grading_database.db")
        stats = pd.read_sql_query("""
            SELECT 
                COUNT(CASE WHEN ai_score IS NOT NULL THEN 1 END) as total_samples,
                COUNT(CASE WHEN human_score IS NOT NULL THEN 1 END) as corrected_samples
            FROM submissions
        """, conn)
        conn.close()
        
        if not stats.empty:
            row = stats.iloc[0]
            print(f"📊 Training Stats:")
            print(f"   Total AI graded: {row['total_samples']}")
            print(f"   Human corrected: {row['corrected_samples']}")
            
            if row['total_samples'] > 0:
                correction_rate = (row['corrected_samples'] / row['total_samples']) * 100
                print(f"   Correction rate: {correction_rate:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Training interface test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_submission_filters():
    """Test the submission filtering functionality"""
    
    print("\n🔍 Testing Submission Filters...")
    
    try:
        mock_grader = MockGrader()
        training_interface = TrainingInterface(mock_grader)
        
        # Test different filters
        filters = [
            ("All Assignments", "All"),
            ("All Assignments", "Needs Review"),
            ("All Assignments", "Already Corrected"),
            ("Assignment 1 - Introduction to R", "All")
        ]
        
        for assignment_filter, status_filter in filters:
            submissions = training_interface.get_submissions_for_review(assignment_filter, status_filter)
            print(f"   {assignment_filter} + {status_filter}: {len(submissions)} submissions")
        
        return True
        
    except Exception as e:
        print(f"❌ Filter test failed: {e}")
        return False

def main():
    """Run training interface tests"""
    
    print("🎯 Testing AI Training Interface")
    print("=" * 50)
    
    tests = [
        ("Training Interface", test_training_interface),
        ("Submission Filters", test_submission_filters)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary:")
    all_passed = True
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed!")
        print("📋 Training interface should now show submissions for review")
        print("🔧 You can now review and correct AI grades in the Streamlit app")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
    
    return all_passed

if __name__ == "__main__":
    main()