#!/usr/bin/env python3
"""
Test all pages to ensure they're pointing to the right places and using correct data sources
"""

import sqlite3
import pandas as pd
import os
import json

class MockGrader:
    """Mock grader for testing"""
    def __init__(self):
        self.db_path = "grading_database.db"
        self.assignments_dir = "assignments"
        self.submissions_dir = "submissions"

def test_database_schema():
    """Test that the database schema is correct and consistent"""
    
    print("🗄️ Testing Database Schema...")
    
    if not os.path.exists("grading_database.db"):
        print("❌ No database found")
        return False
    
    try:
        conn = sqlite3.connect("grading_database.db")
        cursor = conn.cursor()
        
        # Check table structures
        tables_to_check = ['assignments', 'students', 'submissions', 'ai_training_data']
        
        for table in tables_to_check:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            if columns:
                print(f"✅ Table '{table}' exists with {len(columns)} columns")
                for col in columns:
                    print(f"   - {col[1]} ({col[2]})")
            else:
                print(f"❌ Table '{table}' not found")
        
        # Check data consistency
        cursor.execute("""
            SELECT COUNT(*) as total_assignments FROM assignments
        """)
        assignments_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) as total_students FROM students
        """)
        students_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) as total_submissions FROM submissions
        """)
        submissions_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) as graded_submissions 
            FROM submissions 
            WHERE ai_score IS NOT NULL
        """)
        graded_count = cursor.fetchone()[0]
        
        print(f"\n📊 Database Contents:")
        print(f"   Assignments: {assignments_count}")
        print(f"   Students: {students_count}")
        print(f"   Submissions: {submissions_count}")
        print(f"   Graded: {graded_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
        return False

def test_assignment_management():
    """Test assignment management functionality"""
    
    print("\n📝 Testing Assignment Management...")
    
    try:
        from assignment_manager import create_assignment_page, upload_submissions_page
        from assignment_editor import assignment_management_page
        
        print("✅ Assignment management imports working")
        
        # Test database queries used by assignment management
        conn = sqlite3.connect("grading_database.db")
        
        # Test assignment listing query
        assignments = pd.read_sql_query("SELECT id, name FROM assignments ORDER BY created_date DESC", conn)
        print(f"✅ Assignment listing query: {len(assignments)} assignments found")
        
        # Test assignment creation query structure
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(assignments)")
        assignment_columns = [col[1] for col in cursor.fetchall()]
        
        required_columns = ['id', 'name', 'description', 'total_points', 'rubric', 'created_date']
        missing_columns = [col for col in required_columns if col not in assignment_columns]
        
        if missing_columns:
            print(f"⚠️ Missing assignment columns: {missing_columns}")
        else:
            print("✅ Assignment table structure correct")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Assignment management test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_submission_upload():
    """Test submission upload functionality"""
    
    print("\n📤 Testing Submission Upload...")
    
    try:
        # Test student-submission relationship
        conn = sqlite3.connect("grading_database.db")
        
        # Check if submissions reference students correctly
        query = """
            SELECT s.id, s.student_id, st.student_id as student_identifier, st.name
            FROM submissions s
            LEFT JOIN students st ON s.student_id = st.id
            LIMIT 5
        """
        
        results = pd.read_sql_query(query, conn)
        
        if not results.empty:
            print(f"✅ Found {len(results)} submissions with student references")
            
            # Check for orphaned submissions
            orphaned = results[results['student_identifier'].isna()]
            if not orphaned.empty:
                print(f"⚠️ Found {len(orphaned)} orphaned submissions (no matching student)")
            else:
                print("✅ All submissions have valid student references")
        else:
            print("ℹ️ No submissions found to test")
        
        # Test student table structure
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(students)")
        student_columns = [col[1] for col in cursor.fetchall()]
        
        required_student_columns = ['id', 'student_id', 'name', 'email']
        missing_student_columns = [col for col in required_student_columns if col not in student_columns]
        
        if missing_student_columns:
            print(f"⚠️ Missing student columns: {missing_student_columns}")
        else:
            print("✅ Student table structure correct")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Submission upload test failed: {e}")
        return False

def test_grading_interface():
    """Test grading interface functionality"""
    
    print("\n⚡ Testing Grading Interface...")
    
    try:
        from connect_web_interface import grade_submissions_page, generate_pdf_report
        from grading_interface import view_results_page
        
        print("✅ Grading interface imports working")
        
        # Test grading queries
        conn = sqlite3.connect("grading_database.db")
        
        # Test ungraded submissions query
        ungraded = pd.read_sql_query("""
            SELECT s.*, st.name as student_name, st.student_id as student_identifier
            FROM submissions s
            LEFT JOIN students st ON s.student_id = st.id
            WHERE s.ai_score IS NULL
            LIMIT 5
        """, conn)
        
        print(f"✅ Ungraded submissions query: {len(ungraded)} found")
        
        # Test graded submissions query
        graded = pd.read_sql_query("""
            SELECT s.*, st.name as student_name, st.student_id as student_identifier
            FROM submissions s
            LEFT JOIN students st ON s.student_id = st.id
            WHERE s.ai_score IS NOT NULL
            LIMIT 5
        """, conn)
        
        print(f"✅ Graded submissions query: {len(graded)} found")
        
        # Test comprehensive feedback format
        if not graded.empty:
            sample_feedback = graded.iloc[0]['ai_feedback']
            if sample_feedback:
                try:
                    feedback_data = json.loads(sample_feedback)
                    if isinstance(feedback_data, dict) and 'comprehensive_feedback' in feedback_data:
                        print("✅ Comprehensive feedback format detected")
                    elif isinstance(feedback_data, list):
                        print("ℹ️ Legacy feedback format detected")
                    else:
                        print("⚠️ Unknown feedback format")
                except:
                    print("⚠️ Feedback is not JSON format")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Grading interface test failed: {e}")
        return False

def test_training_interface():
    """Test AI training interface functionality"""
    
    print("\n🎯 Testing AI Training Interface...")
    
    try:
        from training_interface import TrainingInterface
        
        mock_grader = MockGrader()
        training_interface = TrainingInterface(mock_grader)
        
        print("✅ Training interface imports working")
        
        # Test submissions for review query
        submissions = training_interface.get_submissions_for_review("All Assignments", "All")
        print(f"✅ Training submissions query: {len(submissions)} found")
        
        # Test training stats query
        conn = sqlite3.connect("grading_database.db")
        stats = pd.read_sql_query("""
            SELECT 
                COUNT(CASE WHEN ai_score IS NOT NULL THEN 1 END) as total_samples,
                COUNT(CASE WHEN human_score IS NOT NULL THEN 1 END) as corrected_samples
            FROM submissions
        """, conn)
        
        if not stats.empty:
            row = stats.iloc[0]
            print(f"✅ Training stats: {row['total_samples']} total, {row['corrected_samples']} corrected")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Training interface test failed: {e}")
        return False

def test_view_results():
    """Test view results functionality"""
    
    print("\n📊 Testing View Results...")
    
    try:
        from grading_interface import view_results_page
        
        print("✅ View results imports working")
        
        # Test results queries
        conn = sqlite3.connect("grading_database.db")
        
        # Test main results query
        results = pd.read_sql_query("""
            SELECT s.*, st.name as student_name, st.student_id as student_identifier
            FROM submissions s
            LEFT JOIN students st ON s.student_id = st.id
            ORDER BY s.submission_date DESC
            LIMIT 10
        """, conn)
        
        print(f"✅ Results query: {len(results)} submissions found")
        
        # Test export query
        export_data = pd.read_sql_query("""
            SELECT s.*, 
                   COALESCE(st.name, 'Unknown') as student_name,
                   st.student_id as student_id_number
            FROM submissions s
            LEFT JOIN students st ON s.student_id = st.id
            ORDER BY st.student_id
            LIMIT 5
        """, conn)
        
        print(f"✅ Export query: {len(export_data)} records for export")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ View results test failed: {e}")
        return False

def test_pdf_generation():
    """Test PDF report generation"""
    
    print("\n📄 Testing PDF Generation...")
    
    try:
        from report_generator import PDFReportGenerator
        
        # Test with sample comprehensive feedback
        sample_result = {
            'total_score': 34.5,
            'max_score': 37.5,
            'comprehensive_feedback': {
                'instructor_comments': 'Test feedback for PDF generation',
                'detailed_feedback': {
                    'reflection_assessment': ['Good critical thinking'],
                    'analytical_strengths': ['Strong analysis'],
                    'recommendations': ['Continue good work']
                }
            },
            'technical_analysis': {
                'code_strengths': ['Good R implementation'],
                'code_suggestions': ['Consider using complete.cases()'],
                'technical_observations': ['Solid programming concepts']
            }
        }
        
        generator = PDFReportGenerator()
        pdf_path = generator.generate_report(
            student_name="Test_Student",
            assignment_id="Test Assignment",
            analysis_result=sample_result
        )
        
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"✅ PDF generated successfully: {file_size:,} bytes")
            return True
        else:
            print("❌ PDF file not created")
            return False
        
    except Exception as e:
        print(f"❌ PDF generation test failed: {e}")
        return False

def main():
    """Run all page tests"""
    
    print("🧪 Testing All Pages and Data Sources")
    print("=" * 60)
    
    tests = [
        ("Database Schema", test_database_schema),
        ("Assignment Management", test_assignment_management),
        ("Submission Upload", test_submission_upload),
        ("Grading Interface", test_grading_interface),
        ("Training Interface", test_training_interface),
        ("View Results", test_view_results),
        ("PDF Generation", test_pdf_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
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
        print("\n🎉 All pages are working correctly!")
        print("📋 All data sources are properly connected")
        print("🔧 The Streamlit app should work without issues")
    else:
        print("\n⚠️ Some issues found. Check the error messages above.")
    
    return all_passed

if __name__ == "__main__":
    main()