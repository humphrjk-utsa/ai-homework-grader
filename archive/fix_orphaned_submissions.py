#!/usr/bin/env python3
"""
Fix orphaned submissions (submissions without matching students)
"""

import sqlite3
import pandas as pd

def fix_orphaned_submissions():
    """Fix submissions that don't have matching student records"""
    
    print("🔧 Fixing Orphaned Submissions...")
    
    conn = sqlite3.connect("grading_database.db")
    cursor = conn.cursor()
    
    # Find orphaned submissions
    orphaned_query = """
        SELECT s.id, s.student_id, s.notebook_path
        FROM submissions s
        LEFT JOIN students st ON s.student_id = st.id
        WHERE st.id IS NULL
    """
    
    orphaned = pd.read_sql_query(orphaned_query, conn)
    
    if orphaned.empty:
        print("✅ No orphaned submissions found")
        conn.close()
        return
    
    print(f"Found {len(orphaned)} orphaned submissions:")
    
    fixed_count = 0
    
    for _, row in orphaned.iterrows():
        submission_id = row['id']
        student_id_value = row['student_id']
        notebook_path = row['notebook_path']
        
        print(f"   Submission {submission_id}: student_id = {student_id_value}")
        
        try:
            # Check if this is a numeric ID that should reference the students table
            if isinstance(student_id_value, (int, float)) or (isinstance(student_id_value, str) and student_id_value.isdigit()):
                # This looks like it should be a foreign key to students table
                student_db_id = int(student_id_value)
                
                # Check if this student ID exists in students table
                cursor.execute("SELECT student_id, name FROM students WHERE id = ?", (student_db_id,))
                student_record = cursor.fetchone()
                
                if student_record:
                    print(f"   ✅ Student ID {student_db_id} exists: {student_record[1]} ({student_record[0]})")
                    fixed_count += 1
                else:
                    print(f"   ⚠️ Student ID {student_db_id} not found in students table")
                    
                    # Create a placeholder student record
                    placeholder_student_id = f"student_{student_db_id}"
                    cursor.execute("""
                        INSERT INTO students (student_id, name, email)
                        VALUES (?, ?, ?)
                    """, (placeholder_student_id, f"Student {student_db_id}", f"{placeholder_student_id}@university.edu"))
                    
                    print(f"   ✅ Created placeholder student: {placeholder_student_id}")
                    fixed_count += 1
            
            else:
                # This is a text student ID - create a student record for it
                text_student_id = str(student_id_value)
                
                # Check if student already exists with this student_id
                cursor.execute("SELECT id FROM students WHERE student_id = ?", (text_student_id,))
                existing_student = cursor.fetchone()
                
                if existing_student:
                    # Update submission to use the correct student database ID
                    cursor.execute("""
                        UPDATE submissions 
                        SET student_id = ? 
                        WHERE id = ?
                    """, (existing_student[0], submission_id))
                    
                    print(f"   ✅ Linked to existing student: {text_student_id}")
                    fixed_count += 1
                
                else:
                    # Create new student record
                    cursor.execute("""
                        INSERT INTO students (student_id, name, email)
                        VALUES (?, ?, ?)
                    """, (text_student_id, f"Student {text_student_id}", f"{text_student_id}@university.edu"))
                    
                    new_student_id = cursor.lastrowid
                    
                    # Update submission to use the new student database ID
                    cursor.execute("""
                        UPDATE submissions 
                        SET student_id = ? 
                        WHERE id = ?
                    """, (new_student_id, submission_id))
                    
                    print(f"   ✅ Created new student and linked: {text_student_id}")
                    fixed_count += 1
        
        except Exception as e:
            print(f"   ❌ Error fixing submission {submission_id}: {e}")
    
    conn.commit()
    
    # Verify the fix
    orphaned_after = pd.read_sql_query(orphaned_query, conn)
    
    print(f"\n📊 Results:")
    print(f"   Fixed: {fixed_count} submissions")
    print(f"   Remaining orphaned: {len(orphaned_after)}")
    
    if orphaned_after.empty:
        print("✅ All orphaned submissions have been fixed!")
    else:
        print("⚠️ Some submissions still orphaned:")
        for _, row in orphaned_after.iterrows():
            print(f"   - Submission {row['id']}: student_id = {row['student_id']}")
    
    conn.close()
    
    return len(orphaned_after) == 0

def verify_student_submission_relationships():
    """Verify that all submissions have valid student relationships"""
    
    print("\n🔍 Verifying Student-Submission Relationships...")
    
    conn = sqlite3.connect("grading_database.db")
    
    # Check all submissions
    query = """
        SELECT 
            s.id as submission_id,
            s.student_id,
            st.id as student_db_id,
            st.student_id as student_identifier,
            st.name as student_name
        FROM submissions s
        LEFT JOIN students st ON s.student_id = st.id
        ORDER BY s.id
    """
    
    results = pd.read_sql_query(query, conn)
    
    total_submissions = len(results)
    valid_relationships = len(results[results['student_db_id'].notna()])
    
    print(f"📊 Relationship Status:")
    print(f"   Total submissions: {total_submissions}")
    print(f"   Valid relationships: {valid_relationships}")
    print(f"   Success rate: {(valid_relationships/total_submissions)*100:.1f}%")
    
    # Show sample relationships
    if not results.empty:
        print(f"\n📋 Sample Relationships:")
        for _, row in results.head(5).iterrows():
            status = "✅" if pd.notna(row['student_db_id']) else "❌"
            print(f"   {status} Submission {row['submission_id']}: {row['student_name']} ({row['student_identifier']})")
    
    conn.close()
    
    return valid_relationships == total_submissions

def main():
    """Fix orphaned submissions and verify relationships"""
    
    print("🔧 Fixing Student-Submission Relationships")
    print("=" * 50)
    
    # Fix orphaned submissions
    fix_success = fix_orphaned_submissions()
    
    # Verify relationships
    verify_success = verify_student_submission_relationships()
    
    if fix_success and verify_success:
        print("\n🎉 All student-submission relationships are now correct!")
        print("📋 The Streamlit app should work properly with all pages")
    else:
        print("\n⚠️ Some issues remain. Check the messages above.")

if __name__ == "__main__":
    main()