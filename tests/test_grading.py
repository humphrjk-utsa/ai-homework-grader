#!/usr/bin/env python3
"""
Test script to debug grading issues
"""

import sys
import os
sys.path.append('.')

from ai_grader import AIGrader
from app import HomeworkGrader
import sqlite3
import pandas as pd

def test_grading_system():
    print("🧪 Testing Homework Grading System")
    print("=" * 50)
    
    try:
        # Initialize grader
        grader = HomeworkGrader()
        ai_grader = AIGrader(grader)
        
        print("✅ Grader initialized")
        
        # Check database
        conn = sqlite3.connect(grader.db_path)
        
        # Check assignments
        assignments = pd.read_sql_query("SELECT * FROM assignments", conn)
        print(f"📋 Found {len(assignments)} assignments")
        
        if not assignments.empty:
            for _, assignment in assignments.iterrows():
                print(f"  • {assignment['name']} (ID: {assignment['id']})")
        
        # Check submissions
        submissions = pd.read_sql_query("SELECT * FROM submissions", conn)
        print(f"📤 Found {len(submissions)} submissions")
        
        if not submissions.empty:
            for _, submission in submissions.iterrows():
                print(f"  • Student: {submission['student_id']}, Assignment: {submission['assignment_id']}")
        
        # Check ungraded submissions
        ungraded = pd.read_sql_query("""
            SELECT s.*, a.name as assignment_name
            FROM submissions s
            JOIN assignments a ON s.assignment_id = a.id
            WHERE s.ai_score IS NULL
        """, conn)
        
        print(f"⏳ Found {len(ungraded)} ungraded submissions")
        
        if not ungraded.empty:
            print("Ungraded submissions:")
            for _, sub in ungraded.iterrows():
                print(f"  • {sub['student_id']} - {sub['assignment_name']}")
                
                # Check if notebook file exists
                if os.path.exists(sub['notebook_path']):
                    print(f"    ✅ Notebook file exists: {sub['notebook_path']}")
                else:
                    print(f"    ❌ Notebook file missing: {sub['notebook_path']}")
        
        conn.close()
        
        # Test AI connection
        print(f"\n🤖 AI Model Status:")
        print(f"  Model: {ai_grader.local_ai.model_name}")
        print(f"  Available: {ai_grader.use_local_ai}")
        
        if ai_grader.use_local_ai:
            memory_status = ai_grader.local_ai.check_model_memory_status()
            print(f"  In Memory: {memory_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sample_grading():
    """Test grading with a sample notebook if available"""
    print("\n🧪 Testing Sample Grading")
    print("=" * 30)
    
    # Check for sample notebooks
    sample_notebooks = [
        "sample_assignment_template.ipynb",
        "sample_solution.ipynb",
        "../assignment/Homework/homework_lesson_1.ipynb"
    ]
    
    for notebook in sample_notebooks:
        if os.path.exists(notebook):
            print(f"📓 Found sample notebook: {notebook}")
            
            try:
                grader = HomeworkGrader()
                ai_grader = AIGrader(grader)
                
                # Try to extract features (this tests the notebook reading)
                features = ai_grader.extract_notebook_features(notebook)
                if features:
                    print(f"  ✅ Successfully extracted features")
                    print(f"    Code cells: {features.get('code_cells', 0)}")
                    print(f"    Markdown cells: {features.get('markdown_cells', 0)}")
                else:
                    print(f"  ❌ Failed to extract features")
                    
            except Exception as e:
                print(f"  ❌ Error processing {notebook}: {e}")
        else:
            print(f"📓 Sample notebook not found: {notebook}")

if __name__ == "__main__":
    success = test_grading_system()
    
    if success:
        test_sample_grading()
    
    print("\n" + "=" * 50)
    print("💡 If you see errors above, that's likely what's causing")
    print("   the 'string error' in the Streamlit interface.")