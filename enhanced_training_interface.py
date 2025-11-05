"""
Enhanced Training Interface
Provides methods for managing AI training data and submissions
"""
import sqlite3
import os
from datetime import datetime

class EnhancedTrainingInterface:
    """Interface for enhanced AI training and review"""
    
    def __init__(self):
        # Use the main grading database, not a separate one
        self.db_path = "grading_database.db"
    
    def get_database_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_assignments(self):
        """Get list of assignments with submission counts"""
        conn = self.get_database_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                a.id,
                a.name as title,
                COUNT(s.id) as submission_count,
                SUM(CASE WHEN s.human_score IS NOT NULL THEN 1 ELSE 0 END) as human_reviewed_count
            FROM assignments a
            LEFT JOIN submissions s ON a.id = s.assignment_id
            GROUP BY a.id, a.name
            ORDER BY a.created_date DESC
        """)
        
        assignments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return assignments
    
    def get_training_stats(self, assignment_id):
        """Get training statistics for an assignment"""
        conn = self.get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN human_score IS NOT NULL THEN 1 ELSE 0 END) as reviewed,
                AVG(ai_score) as avg_ai,
                AVG(CASE WHEN human_score IS NOT NULL THEN human_score ELSE NULL END) as avg_human
            FROM submissions
            WHERE assignment_id = ?
        """, (assignment_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        total = row[0] or 0
        reviewed = row[1] or 0
        avg_ai = row[2] or 0
        avg_human = row[3] or 0
        
        review_pct = (reviewed / total * 100) if total > 0 else 0
        accuracy_pct = 100 - abs(avg_ai - avg_human) / 37.5 * 100 if avg_human > 0 else 0
        
        return {
            'total_submissions': total,
            'human_reviewed': reviewed,
            'review_percentage': round(review_pct, 1),
            'avg_ai_score': round(avg_ai, 1),
            'avg_human_score': round(avg_human, 1),
            'ai_accuracy_percentage': round(accuracy_pct, 1)
        }
    
    def get_submissions(self, assignment_id, filters=None):
        """Get submissions for an assignment with optional filters"""
        conn = self.get_database_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT 
                s.id,
                s.student_id,
                s.notebook_path,
                s.ai_score,
                s.ai_feedback,
                s.human_score,
                s.human_feedback,
                s.final_score,
                s.graded_date,
                s.submission_date,
                COALESCE(s.final_score, s.ai_score) as display_score,
                st.name as student_name
            FROM submissions s
            LEFT JOIN students st ON s.student_id = st.id
            WHERE s.assignment_id = ?
        """
        params = [assignment_id]
        
        # Apply filters
        if filters:
            if filters.get('score_range'):
                min_score, max_score = filters['score_range']
                query += " AND COALESCE(s.final_score, s.ai_score) BETWEEN ? AND ?"
                params.extend([min_score, max_score])
            
            if filters.get('review_status') and filters['review_status'] != 'All':
                if filters['review_status'] == 'AI Only':
                    query += " AND s.human_score IS NULL"
                elif filters['review_status'] == 'Human Reviewed':
                    query += " AND s.human_score IS NOT NULL"
            
            if filters.get('student_search'):
                query += " AND s.student_id LIKE ?"
                params.append(f"%{filters['student_search']}%")
        
        query += " ORDER BY s.submission_date DESC"
        
        cursor.execute(query, params)
        submissions = []
        
        for row in cursor.fetchall():
            sub = dict(row)
            # Add computed fields
            # Use actual student name from students table, fallback to student_id if not found
            if not sub.get('student_name'):
                sub['student_name'] = f"Student {sub['student_id']}"
            sub['ai_percentage'] = (sub['ai_score'] / 37.5 * 100) if sub['ai_score'] else 0
            sub['grade_indicator'] = '✅' if sub['human_score'] is not None else '🤖'
            sub['score_status'] = f"AI: {sub['ai_score']:.1f}" + (f" → Human: {sub['human_score']:.1f}" if sub['human_score'] else "")
            sub['grading_method'] = 'Human' if sub['human_score'] is not None else 'AI'
            
            # Calculate grade category based on final score
            final_score = sub.get('final_score', sub.get('ai_score', 0))
            percentage = (final_score / 37.5 * 100) if final_score else 0
            if percentage >= 90:
                sub['grade_category'] = 'A'
            elif percentage >= 80:
                sub['grade_category'] = 'B'
            elif percentage >= 70:
                sub['grade_category'] = 'C'
            elif percentage >= 60:
                sub['grade_category'] = 'D'
            else:
                sub['grade_category'] = 'F'
            
            # Add review_date field
            sub['review_date'] = sub.get('graded_date', '')
            
            submissions.append(sub)
        
        conn.close()
        return submissions
    
    def save_human_feedback(self, submission_id, score, feedback):
        """Save human feedback for a submission"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE submissions
                SET human_score = ?,
                    human_feedback = ?,
                    final_score = ?,
                    graded_date = ?
                WHERE id = ?
            """, (score, feedback, score, datetime.now(), submission_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False
    
    def get_human_feedback(self, submission_id):
        """Get existing human feedback"""
        conn = self.get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT human_score, human_feedback
            FROM submissions
            WHERE id = ?
        """, (submission_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] is not None:
            return {'score': row[0], 'feedback': row[1]}
        return None
    
    def apply_bulk_operation(self, submission_ids, operation, **kwargs):
        """Apply bulk operation to submissions"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()
            
            if operation == "boost_percentage":
                boost = kwargs.get('boost_percent', 5)
                for sub_id in submission_ids:
                    cursor.execute("""
                        UPDATE submissions
                        SET ai_score = ai_score * (1 + ? / 100.0),
                            final_score = ai_score * (1 + ? / 100.0)
                        WHERE id = ? AND human_score IS NULL
                    """, (boost, boost, sub_id))
            
            elif operation == "apply_curve":
                curve = kwargs.get('curve_points', 2.0)
                for sub_id in submission_ids:
                    cursor.execute("""
                        UPDATE submissions
                        SET ai_score = MIN(37.5, ai_score + ?),
                            final_score = MIN(37.5, COALESCE(final_score, ai_score) + ?)
                        WHERE id = ?
                    """, (curve, curve, sub_id))
            
            conn.commit()
            conn.close()
            return True, f"Applied {operation} to {len(submission_ids)} submissions"
        except Exception as e:
            return False, f"Error: {str(e)}"


def display_interactive_notebook(notebook_path):
    """Display notebook interactively (stub)"""
    import streamlit as st
    st.info(f"Notebook: {notebook_path}")
