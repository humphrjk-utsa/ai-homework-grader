#!/usr/bin/env python3
"""
Add Assignment 7 V3 to the database
"""

import sqlite3
import json
from pathlib import Path

# Database path
db_path = "grading_database.db"

# Read the rubric
rubric_path = "rubrics/assignment_7_rubric_v2.json"
with open(rubric_path, 'r') as f:
    rubric_data = json.load(f)

# Read the template and solution notebooks
template_path = "assignments/a7v3_template.ipynb"
solution_path = "assignments/a7v3_solution.ipynb"

with open(template_path, 'r') as f:
    template_content = f.read()

with open(solution_path, 'r') as f:
    solution_content = f.read()

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if assignment already exists
cursor.execute("SELECT id FROM assignments WHERE name = ?", ("a7v3",))
existing = cursor.fetchone()

if existing:
    print(f"⚠️ Assignment 'a7v3' already exists (ID: {existing[0]})")
    print("Updating existing assignment...")
    
    cursor.execute("""
        UPDATE assignments 
        SET description = ?,
            total_points = ?,
            rubric = ?,
            template_notebook = ?,
            solution_notebook = ?
        WHERE name = ?
    """, (
        "Assignment 7 V3 - String Manipulation and Date/Time Data",
        100,
        json.dumps(rubric_data),
        template_content,
        solution_content,
        "a7v3"
    ))
    
    assignment_id = existing[0]
    print(f"✅ Updated assignment 'a7v3' (ID: {assignment_id})")
else:
    print("Creating new assignment 'a7v3'...")
    
    cursor.execute("""
        INSERT INTO assignments (name, description, total_points, rubric, template_notebook, solution_notebook)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "a7v3",
        "Assignment 7 V3 - String Manipulation and Date/Time Data",
        100,
        json.dumps(rubric_data),
        template_content,
        solution_content
    ))
    
    assignment_id = cursor.lastrowid
    print(f"✅ Created assignment 'a7v3' (ID: {assignment_id})")

conn.commit()
conn.close()

print("\n📋 Assignment Details:")
print(f"   Name: a7v3")
print(f"   Description: Assignment 7 V3 - String Manipulation and Date/Time Data")
print(f"   Total Points: 100")
print(f"   Template: {template_path}")
print(f"   Solution: {solution_path}")
print(f"   Rubric: {rubric_path}")
print("\n✅ Assignment is now available in the dropdown!")
print("🔄 Refresh the web interface to see it.")
