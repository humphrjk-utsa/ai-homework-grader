#!/usr/bin/env python3
"""
Setup Assignment 1 in the database
"""

import sqlite3
import json
import os

def setup_assignment_1():
    """Setup Assignment 1 with proper rubric and solution"""
    
    # Database path (relative to current directory)
    db_path = "grading_database.db"
    
    # Ensure database exists
    if not os.path.exists(db_path):
        print("❌ Database not found. Please run the main app first to create it.")
        return False
    
    # Load rubric
    rubric_path = "assignment_1_rubric.json"
    if not os.path.exists(rubric_path):
        print("❌ Assignment 1 rubric not found")
        return False
    
    with open(rubric_path, 'r') as f:
        rubric_data = json.load(f)
    
    # Solution notebook path
    solution_path = "templates/sample_solution.ipynb"
    if not os.path.exists(solution_path):
        print("⚠️ Solution notebook not found, continuing without it")
        solution_path = None
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if assignment already exists
        cursor.execute("SELECT id FROM assignments WHERE name = ?", ("Assignment 1: Introduction to R",))
        existing = cursor.fetchone()
        
        if existing:
            print("📋 Assignment 1 already exists, updating...")
            cursor.execute("""
                UPDATE assignments 
                SET description = ?, total_points = ?, rubric = ?, solution_notebook = ?
                WHERE name = ?
            """, (
                rubric_data.get("assignment_name", "Introduction to R and Data Analysis"),
                rubric_data.get("total_points", 37.5),
                json.dumps(rubric_data),
                solution_path,
                "Assignment 1: Introduction to R"
            ))
            assignment_id = existing[0]
        else:
            print("📋 Creating Assignment 1...")
            cursor.execute("""
                INSERT INTO assignments (name, description, total_points, rubric, solution_notebook)
                VALUES (?, ?, ?, ?, ?)
            """, (
                "Assignment 1: Introduction to R",
                rubric_data.get("assignment_name", "Introduction to R and Data Analysis"),
                rubric_data.get("total_points", 37.5),
                json.dumps(rubric_data),
                solution_path
            ))
            assignment_id = cursor.lastrowid
        
        conn.commit()
        print(f"✅ Assignment 1 setup complete (ID: {assignment_id})")
        print(f"📊 Total points: {rubric_data.get('total_points', 37.5)}")
        print(f"📝 Rubric categories: {len(rubric_data.get('rubric_categories', {}))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up assignment: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

def setup_sample_student():
    """Setup Logan Balfour as a sample student"""
    
    db_path = "grading_database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if student exists
        cursor.execute("SELECT id FROM students WHERE student_id = ?", ("logan_balfour",))
        existing = cursor.fetchone()
        
        if not existing:
            cursor.execute("""
                INSERT INTO students (student_id, name, email)
                VALUES (?, ?, ?)
            """, (
                "logan_balfour",
                "Logan Balfour", 
                "logan.balfour@example.com"
            ))
            print("👤 Created sample student: Logan Balfour")
        else:
            print("👤 Sample student already exists: Logan Balfour")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up student: {e}")
        return False
    
    finally:
        conn.close()

def main():
    """Main setup function"""
    print("🚀 Setting up Assignment 1 for Homework Grader")
    print("=" * 50)
    
    # Setup assignment
    if setup_assignment_1():
        print("✅ Assignment 1 setup successful")
    else:
        print("❌ Assignment 1 setup failed")
        return
    
    # Setup sample student
    if setup_sample_student():
        print("✅ Sample student setup successful")
    else:
        print("❌ Sample student setup failed")
    
    print("\n🎉 Setup complete! You can now:")
    print("1. Launch the web interface: streamlit run app.py")
    print("2. Upload Logan's notebook in 'Upload Submissions'")
    print("3. Grade assignments in 'Grade Submissions'")
    print("4. Train the AI in 'AI Training'")

if __name__ == "__main__":
    main()