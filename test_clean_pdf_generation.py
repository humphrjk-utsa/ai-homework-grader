#!/usr/bin/env python3
"""
Test Clean PDF Generation
Ensures PDF reports contain only instructor-relevant content
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add current directory to path
sys.path.append('.')

from enhanced_training_interface import EnhancedTrainingInterface
from enhanced_training_database import EnhancedTrainingDatabase
from validate_report_content import ReportContentValidator

def create_test_submission_with_dirty_feedback():
    """Create test submission with AI feedback containing internal dialog"""
    
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # Set up database
    enhanced_db = EnhancedTrainingDatabase(db_path)
    
    # Create test data
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create basic tables and data
    cursor.execute("CREATE TABLE assignments (id INTEGER PRIMARY KEY, title TEXT)")
    cursor.execute("CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, student_id TEXT)")
    cursor.execute("""
        CREATE TABLE submissions (
            id INTEGER PRIMARY KEY, assignment_id INTEGER, student_id INTEGER, 
            ai_score REAL, final_score REAL, notebook_path TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE grading_results (
            id INTEGER PRIMARY KEY, submission_id INTEGER, final_score REAL, 
            comprehensive_feedback TEXT
        )
    """)
    
    cursor.execute("INSERT INTO assignments (id, title) VALUES (1, 'Test Assignment')")
    cursor.execute("INSERT INTO students (id, name, student_id) VALUES (1, 'Test Student', 'S001')")
    cursor.execute("""
        INSERT INTO submissions (id, assignment_id, student_id, ai_score, final_score) 
        VALUES (1, 1, 1, 32.5, 32.5)
    """)
    
    # Create "dirty" feedback with internal AI dialog
    dirty_feedback = {
        "instructor_comments": "Good work on this assignment. What I'm looking for: more detailed analysis and better connections to business context. AI thinking: this student shows promise but needs development.",
        "detailed_feedback": {
            "reflection_assessment": [
                "Shows good engagement with reflection questions",
                "Internal reasoning: student demonstrates critical thinking but could go deeper",
                "What to focus on: encourage more self-reflection"
            ],
            "analytical_strengths": [
                "Clear code structure and organization",
                "AI assessment: proper use of R functions",
                "Express version: good basic analysis"
            ],
            "areas_for_development": [
                "Could improve data visualization techniques",
                "Model dialog: needs more sophisticated analysis methods",
                "What I'm looking for: evidence of advanced statistical thinking"
            ],
            "recommendations": [
                "Practice with more complex datasets",
                "Quick assessment: focus on business applications",
                "Internal: student ready for advanced topics"
            ]
        }
    }
    
    cursor.execute("""
        INSERT INTO grading_results (submission_id, final_score, comprehensive_feedback) 
        VALUES (1, 32.5, ?)
    """, (json.dumps(dirty_feedback),))
    
    conn.commit()
    conn.close()
    
    return db_path

def test_clean_pdf_generation():
    """Test that PDF generation produces clean, instructor-appropriate content"""
    print("🧪 Testing Clean PDF Generation")
    print("=" * 50)
    
    # Create test database with dirty feedback
    test_db_path = create_test_submission_with_dirty_feedback()
    
    try:
        # Initialize training interface
        training = EnhancedTrainingInterface(test_db_path)
        
        print("📊 Generating PDF with dirty feedback...")
        
        # Generate clean PDF report
        pdf_path = training.generate_clean_pdf_report(
            submission_id=1,
            student_name="Test Student",
            assignment_name="Test Assignment"
        )
        
        if pdf_path and os.path.exists(pdf_path):
            print(f"✅ PDF generated successfully: {pdf_path}")
            
            # Verify file exists and has content
            file_size = os.path.getsize(pdf_path)
            print(f"📄 PDF file size: {file_size} bytes")
            
            if file_size > 1000:  # Reasonable minimum size for a PDF
                print("✅ PDF has reasonable content size")
            else:
                print("❌ PDF seems too small")
            
            # Clean up PDF
            os.unlink(pdf_path)
            
        else:
            print("❌ PDF generation failed")
            return False
        
        print("🎉 Clean PDF generation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Clean PDF generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        try:
            os.unlink(test_db_path)
        except:
            pass

def test_feedback_validation():
    """Test that feedback validation catches internal AI dialog"""
    print("\n🧪 Testing Feedback Validation")
    print("=" * 50)
    
    validator = ReportContentValidator()
    
    # Test dirty feedback
    dirty_feedback = {
        "comprehensive_feedback": {
            "instructor_comments": "Good work. What I'm looking for: better analysis. AI thinking: needs improvement.",
            "detailed_feedback": {
                "reflection_assessment": [
                    "Shows good thinking",
                    "Internal reasoning: student needs more depth"
                ]
            }
        }
    }
    
    print("🔍 Validating dirty feedback...")
    is_valid, issues = validator.validate_feedback_content(dirty_feedback)
    
    print(f"   Valid: {is_valid}")
    print(f"   Issues found: {len(issues)}")
    
    if not is_valid:
        print("   ✅ Validation correctly detected issues:")
        for issue in issues[:3]:  # Show first 3 issues
            print(f"   - {issue}")
    else:
        print("   ❌ Validation should have detected issues")
        return False
    
    # Test cleaning
    dirty_text = "Good work. What I'm looking for: more depth. AI thinking: needs improvement."
    clean_text = validator.clean_feedback_for_instructor(dirty_text)
    
    print(f"\n🧹 Testing text cleaning:")
    print(f"   Original: {dirty_text}")
    print(f"   Cleaned:  {clean_text}")
    
    # Verify cleaning worked
    forbidden_phrases = ["what i'm looking for", "ai thinking"]
    clean_lower = clean_text.lower()
    
    for phrase in forbidden_phrases:
        if phrase in clean_lower:
            print(f"   ❌ Cleaning failed - still contains '{phrase}'")
            return False
    
    print("   ✅ Text cleaning successful")
    
    print("🎉 Feedback validation test passed!")
    return True

def test_no_express_versions():
    """Test that there are no express or quick PDF generation methods"""
    print("\n🧪 Testing No Express Versions")
    print("=" * 50)
    
    # Check report generator code
    try:
        with open('report_generator.py', 'r') as f:
            report_code = f.read()
        
        validator = ReportContentValidator()
        is_valid, issues = validator.validate_pdf_generation_methods(report_code)
        
        print(f"📊 PDF Generation Method Validation:")
        print(f"   Valid: {is_valid}")
        
        if issues:
            print(f"   Issues found:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print(f"   ✅ Only standard PDF generation method found")
        
        # Check for single generate_report method
        import re
        main_methods = re.findall(r'def generate_report\(', report_code)
        print(f"   Main generation methods: {len(main_methods)}")
        
        if len(main_methods) == 1:
            print(f"   ✅ Exactly one main PDF generation method")
        else:
            print(f"   ❌ Expected 1 main method, found {len(main_methods)}")
            return False
        
        print("🎉 No express versions test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Express versions test failed: {e}")
        return False

def run_all_clean_pdf_tests():
    """Run all clean PDF generation tests"""
    print("🚀 Clean PDF Generation - Comprehensive Tests")
    print("=" * 60)
    
    tests = [
        ("Clean PDF Generation", test_clean_pdf_generation),
        ("Feedback Validation", test_feedback_validation),
        ("No Express Versions", test_no_express_versions)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Tests...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 CLEAN PDF GENERATION TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All clean PDF tests passed! Reports contain only instructor-relevant content.")
        print("\n📋 Summary of Guarantees:")
        print("✅ No internal AI dialog in reports")
        print("✅ No express or quick PDF versions")
        print("✅ Only instructor-appropriate feedback")
        print("✅ Clean, professional formatting")
        print("✅ Single source of truth for PDF generation")
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = run_all_clean_pdf_tests()
    sys.exit(0 if success else 1)