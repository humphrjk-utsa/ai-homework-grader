"""
Helper utilities for AI grading corrections and feedback generation
"""

class CorrectionHelpers:
    """Helper methods for suggesting score adjustments and generating feedback"""
    
    @staticmethod
    def suggest_score_adjustment(original_score, content, rubric):
        """
        Suggest score adjustments based on content analysis
        
        Args:
            original_score: The AI's original score
            content: The submission content
            rubric: The grading rubric
            
        Returns:
            dict with suggestions
        """
        suggestions = {
            'suggested_score': original_score,
            'confidence': 'medium',
            'reasons': []
        }
        
        # Basic heuristics
        if not content or len(content.strip()) < 50:
            suggestions['suggested_score'] = max(0, original_score - 20)
            suggestions['reasons'].append("Very short submission")
            suggestions['confidence'] = 'high'
        
        return suggestions
    
    @staticmethod
    def generate_feedback_template(score):
        """
        Generate a feedback template based on score
        
        Args:
            score: The numeric score
            
        Returns:
            str: Feedback template
        """
        if score >= 90:
            return "Excellent work! Your solution demonstrates strong understanding of the concepts."
        elif score >= 80:
            return "Good work! Your solution is mostly correct with minor areas for improvement."
        elif score >= 70:
            return "Adequate work. Your solution shows understanding but needs corrections in some areas."
        elif score >= 60:
            return "Your solution needs significant improvements. Please review the requirements carefully."
        else:
            return "Your submission is incomplete or incorrect. Please review the assignment requirements and try again."
    
    @staticmethod
    def smart_feedback_suggestions(human_feedback, ai_feedback, adjustment):
        """
        Generate smart feedback suggestions based on score adjustment
        
        Args:
            human_feedback: Existing human feedback
            ai_feedback: AI-generated feedback
            adjustment: Score adjustment amount
            
        Returns:
            list of feedback suggestions
        """
        suggestions = []
        
        if adjustment > 10:
            suggestions.append("Consider mentioning what the student did better than the AI detected")
        elif adjustment < -10:
            suggestions.append("Consider explaining what issues the AI missed")
        
        if not human_feedback and ai_feedback:
            suggestions.append("You can edit the AI feedback or write your own")
        
        return suggestions
