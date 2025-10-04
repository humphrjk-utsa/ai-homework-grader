#!/usr/bin/env python3
"""
Test Data Consistency
Comprehensive testing to ensure single source of truth and data consistency
"""

import os
import sys
import sqlite3
import tempfile
import json
from datetime import datetime

# Add current directory to path
sys.path.append('.')

from enhanced_training_database import EnhancedTrainingDatabase
from enhanced_training_interface import EnhancedTrainingInterface

def create_test_database_with_inconsistencies():
    """Create a test database with intentional data inconsistencies"""
    
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create basic tables
    cursor.execute("""
        CREATE TABLE assignments (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE students (
            id INTEGER PRIMARY KEY,
            name TEXT,
            student_id TEXT,
            email TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE submissions (
            id INTEGER PRIMARY KEY,
            assignment_id INTEGER,
            student_id INTEGER,
            notebook_path TEXT,
            submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ai_score REAL,
            human_score REAL,  -- This should match human_feedback table
            human_feedback TEXT,  -- This should match human_feedback table
            final_score REAL,  -- This should be derived from human_feedback or grading_results
            FOREIGN KEY (assignment_id) REFERENCES assignments (id),
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE grading_results (
            id INTEGER PRIMARY KEY,
            submission_id INTEGER,
            final_score REAL,
            final_score_percentage REAL,
            grading_method TEXT,
            comprehensive_feedback TEXT,
            FOREIGN KEY (submission_id) REFERENCES submissions (id)
        )
    """)
    
    # Insert sample data
    cursor.execute("""
        INSERT INTO assignments (id, title, description) VALUES 
        (1, 'Test Assignment', 'Test assignment for data consistency')
    """)
    
    cursor.execute("""
        INSERT INTO students (id, name, student_id, email) VALUES 
        (1, 'Alice Johnson', 'S001', 'alice@test.edu'),
        (2, 'Bob Smith', 'S002', 'bob@test.edu'),
        (3, 'Carol Davis', 'S003', 'carol@test.edu')
    """)
    
    # Insert submissions with INTENTIONAL INCONSISTENCIES
    cursor.execute("""
        INSERT INTO submissions (id, assignment_id, student_id, ai_score, human_score, human_feedback, final_score) VALUES 
        (1, 1, 1, 30.0, 32.0, 'Good work', 30.0),  -- final_score doesn't match human_score
        (2, 1, 2, 25.0, NULL, NULL, 25.0),         -- Consistent (no human review)
        (3, 1, 3, 28.0, 30.0, 'Improved', 28.0)   -- final_score doesn't match human_score
    """)
    
    cursor.execute("""
        INSERT INTO grading_results (submission_id, final_score, final_score_percentage, grading_method) VALUES 
        (1, 30.0, 80.0, 'ai_system'),
        (2, 25.0, 66.7, 'ai_system'),
        (3, 28.0, 74.7, 'ai_system')
    """)
    
    conn.commit()
    conn.close()
    
    return db_path

def test_data_consistency_validation():
    """Test data consistency validation and fixing"""
    print("🧪 Testing Data Consistency Validation")
    print("=" * 50)
    
    # Create test database with inconsistencies
    test_db_path = create_test_database_with_inconsistencies()
    
    try:
        # Set up enhanced database (this will create the human_feedback table)
        print("📊 Setting up enhanced database...")
        enhanced_db = EnhancedTrainingDatabase(test_db_path)
        enhanced_db.migrate_existing_data()
        
        # Create some human feedback records that don't match submissions table
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # First, migrate existing human scores to human_feedback table
        cursor.execute("""
            INSERT OR IGNORE INTO human_feedback (submission_id, human_score, human_feedback, instructor_id) 
            SELECT id, human_score, human_feedback, 'instructor'
            FROM submissions 
            WHERE human_score IS NOT NULL
        """)
        
        # Then update with different values to create inconsistencies
        cursor.execute("""
            UPDATE human_feedback 
            SET human_score = 35.0, human_feedback = 'Excellent work after review'
            WHERE submission_id = 1
        """)
        cursor.execute("""
            UPDATE human_feedback 
            SET human_score = 33.0, human_feedback = 'Much better than initial'
            WHERE submission_id = 3
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Test database with inconsistencies created")
        
        # Run validation
        print("\n🔍 Running data consistency validation...")
        results = enhanced_db.validate_data_consistency()
        
        print(f"📊 Validation Results:")
        print(f"   - Total submissions: {results['total_submissions']}")
        print(f"   - Consistent records: {results['consistent_records']}")
        print(f"   - Issues found: {len(results['issues_found'])}")
        print(f"   - Fixes applied: {len(results['fixes_applied'])}")
        
        if results['issues_found']:
            print("\n❌ Issues found:")
            for issue in results['issues_found']:
                print(f"   - {issue}")
        
        if results['fixes_applied']:
            print("\n✅ Fixes applied:")
            for fix in results['fixes_applied']:
                print(f"   - {fix}")
        
        # Verify fixes were applied
        print("\n🔍 Verifying fixes...")
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # Check that final_score now matches human_feedback where it exists
        cursor.execute("""
            SELECT s.id, s.final_score, hf.human_score, gr.final_score as ai_score
            FROM submissions s
            LEFT JOIN human_feedback hf ON s.id = hf.submission_id
            LEFT JOIN grading_results gr ON s.id = gr.submission_id
        """)
        
        all_consistent = True
        for row in cursor.fetchall():
            submission_id, final_score, human_score, ai_score = row
            expected_final = human_score if human_score is not None else ai_score
            
            if final_score != expected_final:
                print(f"   ❌ Submission {submission_id}: final_score={final_score}, expected={expected_final}")
                all_consistent = False
            else:
                print(f"   ✅ Submission {submission_id}: consistent (final_score={final_score})")
        
        conn.close()
        
        if all_consistent:
            print("🎉 All data is now consistent!")
        else:
            print("❌ Some inconsistencies remain")
        
        return all_consistent
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        try:
            os.unlink(test_db_path)
        except:
            pass

def test_single_source_of_truth():
    """Test that the system maintains single source of truth"""
    print("\n🧪 Testing Single Source of Truth")
    print("=" * 50)
    
    # Create clean test database
    db_fd, test_db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    try:
        # Create basic test data first
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # Create basic tables
        cursor.execute("CREATE TABLE assignments (id INTEGER PRIMARY KEY, title TEXT)")
        cursor.execute("CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, student_id TEXT)")
        cursor.execute("""
            CREATE TABLE submissions (
                id INTEGER PRIMARY KEY, assignment_id INTEGER, student_id INTEGER, 
                ai_score REAL, final_score REAL, human_score REAL, human_feedback TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE grading_results (
                id INTEGER PRIMARY KEY, submission_id INTEGER, final_score REAL, 
                final_score_percentage REAL, grading_method TEXT
            )
        """)
        
        cursor.execute("INSERT INTO assignments (id, title) VALUES (1, 'Test Assignment')")
        cursor.execute("INSERT INTO students (id, name, student_id) VALUES (1, 'Test Student', 'S001')")
        cursor.execute("""
            INSERT INTO submissions (id, assignment_id, student_id, ai_score, final_score) 
            VALUES (1, 1, 1, 30.0, 30.0)
        """)
        cursor.execute("""
            INSERT INTO grading_results (submission_id, final_score, final_score_percentage, grading_method) 
            VALUES (1, 30.0, 80.0, 'ai_system')
        """)
        
        conn.commit()
        conn.close()
        
        # Set up enhanced database
        enhanced_db = EnhancedTrainingDatabase(test_db_path)
        
        # Initialize training interface
        training = EnhancedTrainingInterface(test_db_path)
        
        print("📊 Initial state: AI score = 30.0")
        
        # Test 1: Save human feedback
        print("\n1️⃣ Testing save_human_feedback...")
        success = training.save_human_feedback(1, 35.0, "Excellent work!")
        assert success, "Should save human feedback successfully"
        
        # Verify single source of truth
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # Check human_feedback table (authoritative source)
        cursor.execute("SELECT human_score, human_feedback FROM human_feedback WHERE submission_id = 1")
        hf_result = cursor.fetchone()
        assert hf_result[0] == 35.0, "Human feedback table should have correct score"
        assert hf_result[1] == "Excellent work!", "Human feedback table should have correct feedback"
        
        # Check submissions table (derived fields)
        cursor.execute("SELECT final_score, human_score, human_feedback FROM submissions WHERE id = 1")
        sub_result = cursor.fetchone()
        assert sub_result[0] == 35.0, "Submissions.final_score should match human score"
        assert sub_result[1] == 35.0, "Submissions.human_score should match for compatibility"
        assert sub_result[2] == "Excellent work!", "Submissions.human_feedback should match for compatibility"
        
        conn.close()
        print("   ✅ Single source of truth maintained")
        
        # Test 2: Update human feedback
        print("\n2️⃣ Testing update human feedback...")
        success = training.save_human_feedback(1, 37.0, "Outstanding work!")
        assert success, "Should update human feedback successfully"
        
        # Verify update
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT human_score FROM human_feedback WHERE submission_id = 1")
        updated_score = cursor.fetchone()[0]
        assert updated_score == 37.0, "Should update to new score"
        
        cursor.execute("SELECT final_score FROM submissions WHERE id = 1")
        final_score = cursor.fetchone()[0]
        assert final_score == 37.0, "Final score should be updated"
        
        conn.close()
        print("   ✅ Update maintains consistency")
        
        # Test 3: Reset to AI score
        print("\n3️⃣ Testing reset to AI score...")
        success, message = training.apply_bulk_operation([1], "reset_to_ai")
        assert success, "Should reset to AI score successfully"
        
        # Verify reset
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM human_feedback WHERE submission_id = 1")
        hf_count = cursor.fetchone()[0]
        assert hf_count == 0, "Human feedback should be removed"
        
        cursor.execute("SELECT final_score FROM submissions WHERE id = 1")
        final_score = cursor.fetchone()[0]
        assert final_score == 30.0, "Final score should revert to AI score"
        
        conn.close()
        print("   ✅ Reset maintains consistency")
        
        print("🎉 Single source of truth tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Single source of truth test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        try:
            os.unlink(test_db_path)
        except:
            pass

def test_view_consistency():
    """Test that the training_report_view provides consistent data"""
    print("\n🧪 Testing View Consistency")
    print("=" * 50)
    
    # Create test database
    db_fd, test_db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    try:
        # Create test data first
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # Create basic tables
        cursor.execute("CREATE TABLE assignments (id INTEGER PRIMARY KEY, title TEXT)")
        cursor.execute("CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, student_id TEXT)")
        cursor.execute("""
            CREATE TABLE submissions (
                id INTEGER PRIMARY KEY, assignment_id INTEGER, student_id INTEGER, 
                ai_score REAL, final_score REAL, submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notebook_path TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE grading_results (
                id INTEGER PRIMARY KEY, submission_id INTEGER, final_score REAL, 
                final_score_percentage REAL, grading_method TEXT, comprehensive_feedback TEXT
            )
        """)
        
        cursor.execute("INSERT INTO assignments (id, title) VALUES (1, 'Test Assignment')")
        cursor.execute("INSERT INTO students (id, name, student_id) VALUES (1, 'Test Student', 'S001')")
        cursor.execute("""
            INSERT INTO submissions (id, assignment_id, student_id, ai_score, final_score) 
            VALUES (1, 1, 1, 28.0, 28.0)
        """)
        cursor.execute("""
            INSERT INTO grading_results (submission_id, final_score, final_score_percentage, grading_method, comprehensive_feedback) 
            VALUES (1, 28.0, 74.7, 'ai_system', '{}')
        """)
        
        conn.commit()
        
        # Set up enhanced database
        enhanced_db = EnhancedTrainingDatabase(test_db_path)
        
        # Test view without human feedback
        print("📊 Testing view with AI-only score...")
        cursor.execute("SELECT ai_score, human_score, final_score, review_status FROM training_report_view WHERE submission_id = 1")
        result = cursor.fetchone()
        
        assert result[0] == 28.0, "AI score should be 28.0"
        assert result[1] is None, "Human score should be None"
        assert result[2] == 28.0, "Final score should be 28.0"
        assert result[3] == 'AI Only', "Review status should be 'AI Only'"
        print("   ✅ AI-only view correct")
        
        # Add human feedback
        print("📊 Adding human feedback...")
        cursor.execute("""
            INSERT INTO human_feedback (submission_id, human_score, human_feedback) 
            VALUES (1, 32.0, 'Good improvement')
        """)
        conn.commit()
        
        # Test view with human feedback
        cursor.execute("SELECT ai_score, human_score, final_score, review_status FROM training_report_view WHERE submission_id = 1")
        result = cursor.fetchone()
        
        assert result[0] == 28.0, "AI score should remain 28.0"
        assert result[1] == 32.0, "Human score should be 32.0"
        assert result[2] == 32.0, "Final score should be human score (32.0)"
        assert result[3] == 'Boosted', "Review status should be 'Boosted'"
        print("   ✅ Human review view correct")
        
        conn.close()
        
        print("🎉 View consistency tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ View consistency test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        try:
            os.unlink(test_db_path)
        except:
            pass

def run_all_consistency_tests():
    """Run all data consistency tests"""
    print("🚀 Data Consistency - Comprehensive Tests")
    print("=" * 60)
    
    tests = [
        ("Data Consistency Validation", test_data_consistency_validation),
        ("Single Source of Truth", test_single_source_of_truth),
        ("View Consistency", test_view_consistency)
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
    print("📊 DATA CONSISTENCY TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All data consistency tests passed! Single source of truth maintained.")
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = run_all_consistency_tests()
    sys.exit(0 if success else 1)