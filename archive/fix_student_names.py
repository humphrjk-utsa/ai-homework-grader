#!/usr/bin/env python3
"""
Fix student names for bulk uploaded submissions
"""

import sqlite3
import nbformat
import os
import re

def extract_student_info_from_notebook(notebook_path):
    """Extract student information from notebook"""
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        student_info = {
            'name': 'Unknown',
            'id': 'Unknown'
        }
        
        # Look for student info in first few cells
        for i, cell in enumerate(nb.cells[:5]):
            if cell.cell_type == 'markdown':
                content = cell.source
                
                # Look for name patterns
                name_patterns = [
                    r'\*\*Student Name:\*\*\s*\[?([^\]\n]+)\]?',
                    r'Student Name:\s*\[?([^\]\n]+)\]?',
                    r'\*\*Name:\*\*\s*\[?([^\]\n]+)\]?',
                    r'Name:\s*\[?([^\]\n]+)\]?',
                    r'student[:\s]+([^\n\]]+)',
                    r'name[:\s]+([^\n\]]+)'
                ]
                
                for pattern in name_patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        name = match.group(1).strip()
                        # Clean up common placeholder text
                        if name.lower() not in ['your name here', 'name', 'student name', '[your name here]', 'unknown']:
                            student_info['name'] = name
                            break
                
                # Look for ID patterns
                id_patterns = [
                    r'\*\*Student ID:\*\*\s*\[?([^\]\n]+)\]?',
                    r'Student ID:\s*\[?([^\]\n]+)\]?',
                    r'ID:\s*\[?([^\]\n]+)\]?',
                ]
                
                for pattern in id_patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        student_id = match.group(1).strip()
                        if student_id.lower() not in ['your id here', 'id', 'student id', '[your id here]', 'unknown']:
                            student_info['id'] = student_id
                            break
        
        return student_info
    
    except Exception as e:
        print(f"Error reading {notebook_path}: {e}")
        return {'name': 'Unknown', 'id': 'Unknown'}

def fix_student_names():
    """Fix student names for submissions without proper student records"""
    
    conn = sqlite3.connect('grading_database.db')
    cursor = conn.cursor()
    
    # Get submissions without proper student names
    cursor.execute('''
        SELECT s.id, s.student_id, s.notebook_path
        FROM submissions s 
        LEFT JOIN students st ON s.student_id = st.id 
        WHERE st.name IS NULL AND s.notebook_path IS NOT NULL
    ''')
    
    orphaned_submissions = cursor.fetchall()
    print(f"Found {len(orphaned_submissions)} submissions without student names")
    
    fixed_count = 0
    
    for sub_id, student_db_id, notebook_path in orphaned_submissions:
        if os.path.exists(notebook_path):
            print(f"Processing: {notebook_path}")
            
            # Extract student info from notebook
            student_info = extract_student_info_from_notebook(notebook_path)
            student_name = student_info['name']
            
            if student_name != 'Unknown':
                # Create student record with auto-increment ID
                student_id_str = f"student_{student_db_id}"
                
                try:
                    # Insert new student record (let database assign ID)
                    cursor.execute('''
                        INSERT INTO students (student_id, name, email)
                        VALUES (?, ?, ?)
                    ''', (student_id_str, student_name, f"{student_id_str}@university.edu"))
                    
                    new_student_id = cursor.lastrowid
                    
                    # Update the submission to point to the new student record
                    cursor.execute('''
                        UPDATE submissions SET student_id = ? WHERE id = ?
                    ''', (new_student_id, sub_id))
                    
                    print(f"  ✅ Fixed: {student_name} (New ID: {new_student_id})")
                    fixed_count += 1
                    
                except sqlite3.IntegrityError:
                    # Student might already exist, try to find and link
                    cursor.execute('SELECT id FROM students WHERE name = ?', (student_name,))
                    existing_student = cursor.fetchone()
                    if existing_student:
                        cursor.execute('''
                            UPDATE submissions SET student_id = ? WHERE id = ?
                        ''', (existing_student[0], sub_id))
                        print(f"  ✅ Linked: {student_name} (Existing ID: {existing_student[0]})")
                        fixed_count += 1
            else:
                print(f"  ⚠️ Could not extract name from {notebook_path}")
        else:
            print(f"  ❌ File not found: {notebook_path}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Fixed {fixed_count} student records")

if __name__ == "__main__":
    fix_student_names()