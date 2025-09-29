#!/usr/bin/env python3
"""
Fix the web interface to properly connect assignment setup, submission upload, and grading
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import os
from pathlib import Path

def setup_assignment_1():
    """Set up Assignment 1 in the database with proper rubric"""
    
    # Database path (adjust for current directory)
    db_path = "grading_database.db"
    
    # Create database if it doesn't exist
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            total_points INTEGER,
            rubric TEXT,
            template_notebook TEXT,
            solution_notebook TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT,
            email TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER,
            student_id TEXT,
            notebook_path TEXT,
            submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ai_score REAL,
            ai_feedback TEXT,
            human_score REAL,
            human_feedback TEXT,
            final_score REAL,
            graded_date TIMESTAMP,
            FOREIGN KEY (assignment_id) REFERENCES assignments (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_training_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER,
            cell_content TEXT,
            expected_output TEXT,
            human_score REAL,
            ai_score REAL,
            ai_feedback TEXT,
            human_feedback TEXT,
            features TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            corrected_at TIMESTAMP,
            FOREIGN KEY (assignment_id) REFERENCES assignments (id)
        )
    ''')
    
    # Load the Assignment 1 rubric
    rubric_path = "assignment_1_rubric.json"
    with open(rubric_path, 'r') as f:
        rubric_data = json.load(f)
    
    # Insert Assignment 1
    cursor.execute('''
        INSERT OR REPLACE INTO assignments 
        (name, description, total_points, rubric, template_notebook, solution_notebook)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        "Assignment 1 - Introduction to R",
        "Introduction to R programming and basic data analysis",
        37.5,
        json.dumps(rubric_data),
        "templates/sample_assignment_template.ipynb",
        "templates/sample_solution.ipynb"
    ))
    
    # Add Logan as a test student
    cursor.execute('''
        INSERT OR REPLACE INTO students (student_id, name, email)
        VALUES (?, ?, ?)
    ''', ("logan_balfour", "Logan Balfour", "logan.balfour@university.edu"))
    
    conn.commit()
    conn.close()
    
    print("✅ Assignment 1 set up in database")
    print("✅ Database tables created")
    print("✅ Logan Balfour added as test student")

def add_logan_submission():
    """Add Logan's submission to the database"""
    
    db_path = "homework_grader/grading_database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get Assignment 1 ID
    cursor.execute("SELECT id FROM assignments WHERE name = ?", ("Assignment 1 - Introduction to R",))
    assignment_result = cursor.fetchone()
    
    if not assignment_result:
        print("❌ Assignment 1 not found in database")
        return
    
    assignment_id = assignment_result[0]
    
    # Get Logan's student ID
    cursor.execute("SELECT id FROM students WHERE student_id = ?", ("logan_balfour",))
    student_result = cursor.fetchone()
    
    if not student_result:
        print("❌ Logan not found in database")
        return
    
    student_db_id = student_result[0]
    
    # Add Logan's submission
    notebook_path = "Balfour_Logan_homework_lesson_1.ipynb"
    
    cursor.execute('''
        INSERT OR REPLACE INTO submissions 
        (assignment_id, student_id, notebook_path)
        VALUES (?, ?, ?)
    ''', (assignment_id, student_db_id, notebook_path))
    
    conn.commit()
    conn.close()
    
    print("✅ Logan's submission added to database")

def test_web_interface():
    """Test that the web interface can access the data"""
    
    db_path = "grading_database.db"
    
    if not os.path.exists(db_path):
        print("❌ Database not found")
        return False
    
    conn = sqlite3.connect(db_path)
    
    # Test assignments
    assignments = pd.read_sql_query("SELECT * FROM assignments", conn)
    print(f"📋 Assignments in database: {len(assignments)}")
    
    # Test students  
    students = pd.read_sql_query("SELECT * FROM students", conn)
    print(f"👥 Students in database: {len(students)}")
    
    # Test submissions
    submissions = pd.read_sql_query("SELECT * FROM submissions", conn)
    print(f"📤 Submissions in database: {len(submissions)}")
    
    conn.close()
    
    if len(assignments) > 0 and len(students) > 0 and len(submissions) > 0:
        print("✅ Web interface should work properly")
        return True
    else:
        print("❌ Missing data for web interface")
        return False

def main():
    """Set up everything for the web interface"""
    
    print("🔧 Setting up web interface...")
    
    # Create directories
    os.makedirs("assignments", exist_ok=True)
    os.makedirs("submissions", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # Set up Assignment 1
    setup_assignment_1()
    
    # Add Logan's submission
    add_logan_submission()
    
    # Test the setup
    if test_web_interface():
        print("\n🎉 Web interface setup complete!")
        print("\n🚀 To launch the web interface:")
        print("   cd homework_grader")
        print("   streamlit run app.py")
        print("\n📋 You can now:")
        print("   • View Assignment 1 in 'Assignment Management'")
        print("   • See Logan's submission in 'Upload Submissions'")
        print("   • Grade Logan's work in 'Grade Submissions'")
        print("   • Train the AI in 'AI Training'")
    else:
        print("\n❌ Setup failed - check the errors above")

if __name__ == "__main__":
    main()