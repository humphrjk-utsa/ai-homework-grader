"""
Helper utilities for handling alternative solution approaches
"""
import streamlit as st

class AlternativeApproachHandler:
    """Helper methods for analyzing and handling alternative solution approaches"""
    
    @staticmethod
    def show_approach_flexibility_settings():
        """Display settings for approach flexibility"""
        st.subheader("⚙️ Approach Flexibility Settings")
        st.info("Configure how the AI handles different solution approaches.")
        
        st.checkbox("Allow alternative algorithms", value=True)
        st.checkbox("Accept different data structures", value=True)
        st.checkbox("Flexible code style", value=True)
        
        st.slider("Similarity threshold", 0.0, 1.0, 0.7, 
                 help="How similar must the approach be to the solution?")
    
    @staticmethod
    def create_approach_examples():
        """Interface for creating approach examples"""
        st.subheader("📚 Create Approach Examples")
        st.info("Add examples of acceptable alternative approaches.")
        
        st.text_area("Example approach code", height=200)
        st.text_input("Approach description")
        st.button("Add Example")
    
    @staticmethod
    def analyze_approach_differences(student_code, solution_code, language):
        """
        Analyze differences between student and solution approaches
        
        Args:
            student_code: Student's code
            solution_code: Solution code
            language: Programming language
            
        Returns:
            list of differences
        """
        differences = []
        
        # Basic analysis
        if len(student_code) < len(solution_code) * 0.5:
            differences.append({
                'type': 'Length',
                'severity': 'warning',
                'note': 'Student solution is significantly shorter'
            })
        
        return differences
    
    @staticmethod
    def generate_alternative_approach_feedback(differences):
        """
        Generate feedback about alternative approaches
        
        Args:
            differences: List of differences found
            
        Returns:
            str: Feedback text
        """
        if not differences:
            return "Your approach matches the expected solution well."
        
        feedback = "**Approach Analysis:**\n\n"
        for diff in differences:
            feedback += f"- {diff['type']}: {diff['note']}\n"
        
        return feedback
