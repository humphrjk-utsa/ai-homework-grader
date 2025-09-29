#!/usr/bin/env python3
"""
Test CSV export functionality
"""

import sqlite3
import pandas as pd
from datetime import datetime

def test_csv_export():
    """Test the CSV export functionality"""
    
    # Connect to database
    conn = sqlite3.connect('homework_grader.db')
    
    # Get enhanced data with proper student information
    enhanced_data = pd.read_sql_query("""
        SELECT s.*, 
               COALESCE(st.name, 'Unknown') as student_name,
               st.student_id as student_id_number
        FROM submissions s
        LEFT JOIN students st ON s.student_id = st.id
        WHERE s.assignment_id = 1
        ORDER BY st.student_id
    """, conn)
    conn.close()
    
    if enhanced_data.empty:
        print("No submissions found for testing.")
        return
    
    # Clean and validate student names
    def clean_student_name(row):
        name = row['student_name']
        student_id = row['student_id_number']
        
        # Handle malformed names (like "** [YOUR NAME HERE")
        if pd.isna(name) or name == 'Unknown' or '**' in str(name) or '[YOUR NAME HERE' in str(name):
            return f"Student_{student_id}" if student_id else "Unknown_Student"
        
        return str(name).strip()
    
    # Apply name cleaning
    enhanced_data['cleaned_student_name'] = enhanced_data.apply(clean_student_name, axis=1)
    
    # Handle missing scores
    enhanced_data['ai_score'] = enhanced_data['ai_score'].fillna(0).round(2)
    enhanced_data['human_score'] = enhanced_data['human_score'].fillna('')
    enhanced_data['final_score'] = enhanced_data['final_score'].fillna(enhanced_data['ai_score']).round(2)
    
    # Format submission date
    enhanced_data['submission_date'] = pd.to_datetime(enhanced_data['submission_date']).dt.strftime('%Y-%m-%d %H:%M')
    
    # Create final export
    final_export = enhanced_data[[
        'student_id_number', 'cleaned_student_name', 'ai_score', 'human_score', 'final_score', 'submission_date'
    ]].rename(columns={
        'student_id_number': 'Student ID',
        'cleaned_student_name': 'Student Name',
        'ai_score': 'AI Score', 
        'human_score': 'Manual Score',
        'final_score': 'Final Score',
        'submission_date': 'Submission Date'
    })
    
    # Sort by Student ID
    final_export = final_export.sort_values('Student ID')
    
    # Generate CSV
    csv_content = final_export.to_csv(index=False)
    
    # Save test file
    test_filename = f"test_gradebook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(test_filename, 'w') as f:
        f.write(csv_content)
    
    print(f"✅ CSV export test successful!")
    print(f"📁 Test file saved: {test_filename}")
    print(f"📊 Records exported: {len(final_export)}")
    print("\n📋 Sample data:")
    print(final_export.head().to_string(index=False))
    
    # Show statistics
    graded_count = len(final_export[final_export['AI Score'] > 0])
    avg_score = final_export[final_export['AI Score'] > 0]['AI Score'].mean() if graded_count > 0 else 0
    
    print(f"\n📈 Statistics:")
    print(f"   Total Students: {len(final_export)}")
    print(f"   Graded: {graded_count}")
    print(f"   Average Score: {avg_score:.1f}/37.5")

if __name__ == "__main__":
    test_csv_export()