import streamlit as st
import sqlite3
import pandas as pd
import json
from datetime import datetime

class CorrectionHelpers:
    """Helper functions for making corrections more efficient"""
    
    @staticmethod
    def suggest_score_adjustment(ai_score, student_code, rubric_data):
        """Suggest score adjustments based on common patterns"""
        suggestions = []
        
        # Check for common issues
        if "error" in student_code.lower() or "traceback" in student_code.lower():
            if ai_score > 70:
                suggestions.append("Consider lowering score due to execution errors")
        
        # Check for incomplete work
        if len(student_code.strip()) < 50:
            if ai_score > 60:
                suggestions.append("Very short response - may need lower score")
        
        # Check for good practices
        if "library(" in student_code or "install.packages(" in student_code:
            if ai_score < 80:
                suggestions.append("Student shows good R practices - consider higher score")
        
        return suggestions
    
    @staticmethod
    def generate_feedback_template(score_range, common_issues=None):
        """Generate feedback templates based on score range"""
        
        if score_range >= 90:
            template = "Excellent work! Your code demonstrates a strong understanding of the concepts. "
        elif score_range >= 80:
            template = "Good job! Your solution shows solid understanding with room for minor improvements. "
        elif score_range >= 70:
            template = "Nice effort! You're on the right track, but there are a few areas to strengthen. "
        elif score_range >= 60:
            template = "You've made a good start, but there are several important concepts to review. "
        else:
            template = "This assignment needs significant revision. Let's work together to improve your understanding. "
        
        # Add specific suggestions based on common issues
        if common_issues:
            if "execution_error" in common_issues:
                template += "Make sure to test your code before submitting to catch any errors. "
            if "incomplete" in common_issues:
                template += "Try to complete all parts of the assignment for full credit. "
            if "no_comments" in common_issues:
                template += "Adding comments to explain your code will help demonstrate your understanding. "
        
        return template
    
    @staticmethod
    def batch_correction_interface(submissions_df):
        """Interface for making batch corrections"""
        st.subheader("Batch Correction Tools")
        
        # Quick filters for common correction types
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Flag High Scores (>95)"):
                high_scores = submissions_df[submissions_df['ai_score'] > 95]
                st.write(f"Found {len(high_scores)} submissions with scores > 95")
                return high_scores
        
        with col2:
            if st.button("Flag Low Scores (<50)"):
                low_scores = submissions_df[submissions_df['ai_score'] < 50]
                st.write(f"Found {len(low_scores)} submissions with scores < 50")
                return low_scores
        
        with col3:
            if st.button("Flag Large Score Jumps"):
                # This would compare to previous assignments
                st.write("Feature coming soon!")
        
        return None
    
    @staticmethod
    def correction_analytics(grader_db_path):
        """Show analytics about correction patterns"""
        conn = sqlite3.connect(grader_db_path)
        
        # Get correction patterns
        corrections = pd.read_sql_query("""
            SELECT 
                ai_score,
                human_score,
                (human_score - ai_score) as adjustment,
                human_feedback,
                assignment_id
            FROM ai_training_data
            WHERE human_score IS NOT NULL
        """, conn)
        
        conn.close()
        
        if corrections.empty:
            return None
        
        # Analyze patterns
        avg_adjustment = corrections['adjustment'].mean()
        std_adjustment = corrections['adjustment'].std()
        
        # Common adjustment ranges
        large_increases = len(corrections[corrections['adjustment'] > 10])
        large_decreases = len(corrections[corrections['adjustment'] < -10])
        minor_adjustments = len(corrections[corrections['adjustment'].abs() <= 5])
        
        return {
            'avg_adjustment': avg_adjustment,
            'std_adjustment': std_adjustment,
            'large_increases': large_increases,
            'large_decreases': large_decreases,
            'minor_adjustments': minor_adjustments,
            'total_corrections': len(corrections)
        }
    
    @staticmethod
    def smart_feedback_suggestions(student_code, ai_feedback, score_adjustment):
        """Suggest improvements to feedback based on correction patterns"""
        suggestions = []
        
        # If score was increased significantly
        if score_adjustment > 10:
            suggestions.append("Consider adding more positive reinforcement to the feedback")
            suggestions.append("Highlight what the student did well")
        
        # If score was decreased significantly  
        elif score_adjustment < -10:
            suggestions.append("Add constructive guidance for improvement")
            suggestions.append("Be specific about what needs to be fixed")
        
        # Check feedback tone
        if ai_feedback and len(ai_feedback) > 0:
            if "wrong" in ai_feedback.lower() or "incorrect" in ai_feedback.lower():
                suggestions.append("Consider softer language: 'needs revision' instead of 'wrong'")
            
            if "good" not in ai_feedback.lower() and "nice" not in ai_feedback.lower():
                suggestions.append("Add some positive elements to balance the feedback")
        
        return suggestions