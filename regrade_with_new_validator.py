#!/usr/bin/env python3
"""
Regrade submissions using the new flexible partial credit validator
"""

import sqlite3
import json
from validators.rubric_driven_validator import RubricDrivenValidator
from business_analytics_grader_v2 import BusinessAnalyticsGraderV2

def regrade_assignment_7_submissions():
    """Regrade all Assignment 7 v3 submissions with new validator"""
    
    conn = sqlite3.connect('grading_database.db')
    cursor = conn.cursor()
    
    # Get all a7v3 submissions
    cursor.execute("""
        SELECT s.id, s.student_id, s.notebook_path, s.ai_score, s.final_score
        FROM submissions s
        JOIN assignments a ON s.assignment_id = a.id
        WHERE a.name = 'a7v3'
    """)
    
    submissions = cursor.fetchall()
    
    if not submissions:
        print("No a7v3 submissions found")
        return
    
    print(f"Found {len(submissions)} Assignment 7 v3 submissions to regrade")
    print("="*80)
    
    # Initialize validator
    rubric_path = 'rubrics/assignment_7_rubric_v2.json'
    solution_path = 'data/raw/homework_lesson_7_string_datetime_SOLUTION_v2.ipynb'
    
    grader = BusinessAnalyticsGraderV2(
        rubric_path=rubric_path,
        solution_path=solution_path
    )
    
    results = []
    
    for sub_id, student_id, nb_path, old_ai_score, old_final_score in submissions:
        print(f"\nRegrading: {student_id}")
        print(f"  Notebook: {nb_path}")
        print(f"  Old AI Score: {old_ai_score}")
        
        try:
            # Run new grading
            result = grader.grade_assignment(nb_path)
            new_score = result['validation_results']['final_score']
            
            print(f"  New Score: {new_score:.1f}/100")
            print(f"  Change: {new_score - (old_ai_score or 0):+.1f} points")
            
            results.append({
                'id': sub_id,
                'student_id': student_id,
                'old_score': old_ai_score,
                'new_score': new_score,
                'change': new_score - (old_ai_score or 0),
                'result': result
            })
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue
    
    # Summary
    print("\n" + "="*80)
    print("REGRADING SUMMARY")
    print("="*80)
    
    for r in results:
        print(f"\n{r['student_id']}:")
        print(f"  Old: {r['old_score']:.1f} → New: {r['new_score']:.1f} ({r['change']:+.1f})")
    
    # Ask if should update database
    print("\n" + "="*80)
    response = input("Update database with new scores? (yes/no): ")
    
    if response.lower() == 'yes':
        for r in results:
            cursor.execute("""
                UPDATE submissions
                SET ai_score = ?,
                    ai_feedback = ?,
                    final_score = ?
                WHERE id = ?
            """, (
                r['new_score'],
                json.dumps(r['result']),
                r['new_score'],  # Update final score too if no human score
                r['id']
            ))
        
        conn.commit()
        print("✅ Database updated with new scores")
    else:
        print("❌ Database not updated")
    
    conn.close()

if __name__ == '__main__':
    regrade_assignment_7_submissions()
