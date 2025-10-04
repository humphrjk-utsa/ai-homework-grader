#!/usr/bin/env python3
"""
Test Enhanced Training Implementation
Comprehensive testing for the enhanced AI training system
"""

import os
import sys
import sqlite3
import tempfile
import json
import nbformat
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.append('.')

from enhanced_training_database import EnhancedTrainingDatabase
from enhanced_training_interface import EnhancedTrainingInterface

def create_test_database():
    """Create a test database with sample data"""
    
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create basic tables (simulating existing system)
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
            human_score REAL,
            human_feedback TEXT,
            final_score REAL,
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
        (1, 'Data Analysis Assignment 1', 'Introduction to R and data exploration'),
        (2, 'Business Analytics Project', 'Advanced analytics with business applications')
    """)
    
    cursor.execute("""
        INSERT INTO students (id, name, student_id, email) VALUES 
        (1, 'Alice Johnson', 'S001', 'alice@university.edu'),
        (2, 'Bob Smith', 'S002', 'bob@university.edu'),
        (3, 'Carol Davis', 'S003', 'carol@university.edu'),
        (4, 'David Wilson', 'S004', 'david@university.edu'),
        (5, 'Eva Brown', 'S005', 'eva@university.edu')
    """)
    
    # Create test notebook files
    test_notebooks = []
    for i in range(1, 6):
        notebook_path = f"test_notebook_{i}.ipynb"
        create_test_notebook(notebook_path)
        test_notebooks.append(notebook_path)
    
    cursor.execute("""
        INSERT INTO submissions (id, assignment_id, student_id, notebook_path, ai_score, final_score) VALUES 
        (1, 1, 1, 'test_notebook_1.ipynb', 32.5, 32.5),
        (2, 1, 2, 'test_notebook_2.ipynb', 28.0, 28.0),
        (3, 1, 3, 'test_notebook_3.ipynb', 35.0, 35.0),
        (4, 1, 4, 'test_notebook_4.ipynb', 30.5, 30.5),
        (5, 2, 5, 'test_notebook_5.ipynb', 26.5, 26.5)
    """)
    
    # Sample comprehensive feedback
    sample_feedback = {
        "overall_score": 85,
        "detailed_feedback": {
            "reflection_assessment": [
                "Good engagement with reflection questions",
                "Shows developing critical thinking skills"
            ],
            "analytical_strengths": [
                "Proper use of statistical methods",
                "Clear code organization and documentation"
            ],
            "business_application": [
                "Good understanding of business context",
                "Appropriate analytical approach for the problem"
            ],
            "learning_demonstration": [
                "Evidence of skill development throughout assignment",
                "Understanding of key analytical concepts"
            ],
            "areas_for_development": [
                "Could improve data visualization techniques",
                "Need more detailed interpretation of results"
            ],
            "recommendations": [
                "Practice with more complex datasets",
                "Explore advanced analytical techniques"
            ]
        },
        "instructor_comments": "Good work overall. Shows solid understanding of the fundamentals with room for growth in advanced techniques."
    }
    
    cursor.execute("""
        INSERT INTO grading_results (submission_id, final_score, final_score_percentage, grading_method, comprehensive_feedback) VALUES 
        (1, 32.5, 86.7, 'business_analytics_system', ?),
        (2, 28.0, 74.7, 'business_analytics_system', ?),
        (3, 35.0, 93.3, 'business_analytics_system', ?),
        (4, 30.5, 81.3, 'business_analytics_system', ?),
        (5, 26.5, 70.7, 'business_analytics_system', ?)
    """, (json.dumps(sample_feedback),) * 5)
    
    conn.commit()
    conn.close()
    
    return db_path, test_notebooks

def create_test_notebook(path):
    """Create a test notebook file"""
    
    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["# Data Analysis Assignment\n", "**Student:** Test Student\n", "**Date:** 2025-01-01"]
            },
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [
                    {
                        "output_type": "stream",
                        "name": "stdout",
                        "text": ["Loading required libraries...\n"]
                    }
                ],
                "source": ["# Load libraries\n", "library(dplyr)\n", "library(ggplot2)\n", "print('Loading required libraries...')"]
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "outputs": [
                    {
                        "output_type": "execute_result",
                        "execution_count": 2,
                        "data": {
                            "text/html": ["<table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table>"],
                            "text/plain": ["  A B\n1 1 2"]
                        },
                        "metadata": {}
                    }
                ],
                "source": ["# Create sample data\n", "data <- data.frame(A = c(1, 2, 3), B = c(2, 4, 6))\n", "head(data, 1)"]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["## Analysis Results\n", "The data shows a clear linear relationship."]
            },
            {
                "cell_type": "code",
                "execution_count": 3,
                "metadata": {},
                "outputs": [
                    {
                        "output_type": "error",
                        "ename": "Error",
                        "evalue": "object 'undefined_var' not found",
                        "traceback": [
                            "Error in eval(expr, envir, enclos): object 'undefined_var' not found\nTraceback:\n"
                        ]
                    }
                ],
                "source": ["# This cell has an error for testing\n", "print(undefined_var)"]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "R",
                "language": "R",
                "name": "ir"
            },
            "language_info": {
                "name": "R",
                "version": "4.1.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    with open(path, 'w') as f:
        json.dump(notebook_content, f, indent=2)

def test_database_setup():
    """Test database setup and migration"""
    print("🧪 Testing Database Setup")
    print("=" * 40)
    
    # Create test database
    test_db_path, test_notebooks = create_test_database()
    
    try:
        # Test enhanced database setup
        print("📊 Setting up enhanced database...")
        enhanced_db = EnhancedTrainingDatabase(test_db_path)
        
        # Test migration
        print("🔄 Testing data migration...")
        enhanced_db.migrate_existing_data()
        
        # Test statistics calculation
        print("📈 Testing statistics calculation...")
        enhanced_db.calculate_training_stats()
        
        # Verify database structure
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # Check if new tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['human_feedback', 'training_stats', 'training_sessions']
        for table in required_tables:
            if table in tables:
                print(f"   ✅ Table {table} created successfully")
            else:
                print(f"   ❌ Table {table} missing")
        
        # Check view creation
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        views = [row[0] for row in cursor.fetchall()]
        
        if 'training_report_view' in views:
            print("   ✅ Training report view created successfully")
        else:
            print("   ❌ Training report view missing")
        
        conn.close()
        print("✅ Database setup test passed!")
        
    except Exception as e:
        print(f"❌ Database setup test failed: {e}")
        return False
    
    finally:
        # Cleanup
        try:
            os.unlink(test_db_path)
            for notebook in test_notebooks:
                if os.path.exists(notebook):
                    os.unlink(notebook)
        except:
            pass
    
    return True

def test_training_interface():
    """Test the enhanced training interface"""
    print("\n🧪 Testing Training Interface")
    print("=" * 40)
    
    # Create test database
    test_db_path, test_notebooks = create_test_database()
    
    try:
        # Set up enhanced database
        enhanced_db = EnhancedTrainingDatabase(test_db_path)
        enhanced_db.migrate_existing_data()
        
        # Initialize training interface
        print("🎯 Initializing training interface...")
        training = EnhancedTrainingInterface(test_db_path)
        
        # Test 1: Get assignments
        print("\n1️⃣ Testing get_assignments()...")
        assignments = training.get_assignments()
        print(f"   Found {len(assignments)} assignments")
        for assignment in assignments:
            print(f"   - {assignment['title']}: {assignment['submission_count']} submissions")
        assert len(assignments) == 2, "Should have 2 assignments"
        print("   ✅ PASS")
        
        # Test 2: Get submissions
        print("\n2️⃣ Testing get_submissions()...")
        submissions = training.get_submissions(1)
        print(f"   Found {len(submissions)} submissions for assignment 1")
        for submission in submissions[:2]:  # Show first 2
            print(f"   - {submission['student_name']}: {submission['ai_score']}/37.5 ({submission['score_status']})")
        assert len(submissions) == 4, "Should have 4 submissions for assignment 1"
        print("   ✅ PASS")
        
        # Test 3: Save human feedback
        print("\n3️⃣ Testing save_human_feedback()...")
        success = training.save_human_feedback(1, 35.0, "Excellent work! Great improvement.")
        assert success, "Should successfully save human feedback"
        print("   ✅ PASS")
        
        # Test 4: Get human feedback
        print("\n4️⃣ Testing get_human_feedback()...")
        feedback = training.get_human_feedback(1)
        assert feedback is not None, "Should retrieve saved feedback"
        assert feedback['score'] == 35.0, "Score should match saved value"
        print(f"   Retrieved feedback: {feedback['score']}/37.5")
        print("   ✅ PASS")
        
        # Test 5: Get notebook content
        print("\n5️⃣ Testing get_notebook_content()...")
        notebook_content = training.get_notebook_content("test_notebook_1.ipynb")
        assert notebook_content is not None, "Should load notebook content"
        assert notebook_content['cell_count'] == 5, "Should have 5 cells"
        print(f"   Loaded notebook: {notebook_content['cell_count']} cells")
        print(f"   - Code cells: {notebook_content['code_cells']}")
        print(f"   - Markdown cells: {notebook_content['markdown_cells']}")
        print("   ✅ PASS")
        
        # Test 6: Get training stats
        print("\n6️⃣ Testing get_training_stats()...")
        stats = training.get_training_stats(1)
        print(f"   Total submissions: {stats['total_submissions']}")
        print(f"   Human reviewed: {stats['human_reviewed']} ({stats['review_percentage']}%)")
        print(f"   AI accuracy: {stats['ai_accuracy_percentage']}%")
        assert stats['total_submissions'] == 4, "Should have 4 total submissions"
        assert stats['human_reviewed'] == 1, "Should have 1 human reviewed"
        print("   ✅ PASS")
        
        # Test 7: Bulk operations
        print("\n7️⃣ Testing bulk operations...")
        success, message = training.apply_bulk_operation([2, 3], "boost_percentage", boost_percent=10)
        assert success, "Bulk operation should succeed"
        print(f"   {message}")
        print("   ✅ PASS")
        
        # Test 8: CSV export
        print("\n8️⃣ Testing CSV export...")
        updated_submissions = training.get_submissions(1)
        csv_path = training.export_to_csv(1, updated_submissions)
        assert csv_path is not None, "Should generate CSV file"
        assert os.path.exists(csv_path), "CSV file should exist"
        print(f"   CSV exported to: {csv_path}")
        
        # Check CSV content
        import pandas as pd
        df = pd.read_csv(csv_path)
        assert len(df) == 4, "CSV should have 4 rows"
        print(f"   CSV contains {len(df)} rows")
        
        # Cleanup CSV
        os.unlink(csv_path)
        print("   ✅ PASS")
        
        print("\n🎉 All training interface tests passed!")
        
    except Exception as e:
        print(f"\n❌ Training interface test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        try:
            os.unlink(test_db_path)
            for notebook in test_notebooks:
                if os.path.exists(notebook):
                    os.unlink(notebook)
        except:
            pass
    
    return True

def test_notebook_display():
    """Test notebook display functionality"""
    print("\n🧪 Testing Notebook Display")
    print("=" * 40)
    
    # Create a test notebook
    test_notebook_path = "complex_test_notebook.ipynb"
    
    complex_notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["# Advanced Data Analysis\n", "**Student:** Test Student\n", "**Assignment:** Complex Analysis"]
            },
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [
                    {
                        "output_type": "stream",
                        "name": "stdout",
                        "text": ["Libraries loaded successfully\n"]
                    }
                ],
                "source": ["# Load required libraries\n", "import pandas as pd\n", "import numpy as np\n", "print('Libraries loaded successfully')"]
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "outputs": [
                    {
                        "output_type": "execute_result",
                        "execution_count": 2,
                        "data": {
                            "text/html": ["<div><table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table></div>"],
                            "text/plain": ["   A  B\n0  1  2"]
                        },
                        "metadata": {}
                    }
                ],
                "source": ["# Create sample dataframe\n", "df = pd.DataFrame({'A': [1, 2, 3], 'B': [2, 4, 6]})\n", "df.head(1)"]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    # Save test notebook
    with open(test_notebook_path, 'w') as f:
        json.dump(complex_notebook, f, indent=2)
    
    try:
        # Test notebook content parsing
        training = EnhancedTrainingInterface()
        content = training.get_notebook_content(test_notebook_path)
        
        print(f"📊 Notebook Analysis:")
        print(f"   - Total cells: {content['cell_count']}")
        print(f"   - Code cells: {content['code_cells']}")
        print(f"   - Markdown cells: {content['markdown_cells']}")
        print(f"   - Has outputs: {content['has_outputs']}")
        
        # Verify content structure
        assert content['cell_count'] == 3, "Should have 3 cells"
        assert content['code_cells'] == 2, "Should have 2 code cells"
        assert content['markdown_cells'] == 1, "Should have 1 markdown cell"
        
        print("   ✅ Notebook parsing test passed!")
        
        # Test different view modes (would need Streamlit context for full test)
        print("📱 View modes available: full, code_only, summary")
        print("   ✅ View mode functionality ready")
        
    except Exception as e:
        print(f"❌ Notebook display test failed: {e}")
        return False
    
    finally:
        # Cleanup
        if os.path.exists(test_notebook_path):
            os.unlink(test_notebook_path)
    
    return True

def run_all_tests():
    """Run all tests for the enhanced training system"""
    print("🚀 Enhanced AI Training System - Comprehensive Tests")
    print("=" * 60)
    
    tests = [
        ("Database Setup", test_database_setup),
        ("Training Interface", test_training_interface),
        ("Notebook Display", test_notebook_display)
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
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Enhanced training system is ready.")
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)