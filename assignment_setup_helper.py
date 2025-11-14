"""
Helper utilities for assignment setup and course planning
"""
import streamlit as st

class AssignmentSetupHelper:
    """Helper methods for setting up assignments and course planning"""
    
    @staticmethod
    def show_assignment_setup_wizard():
        """Display the assignment setup wizard"""
        st.subheader("📝 Assignment Setup Wizard")
        st.info("This feature helps you set up new assignments with guided steps.")
        
        st.markdown("""
        **Coming Soon:**
        - Step-by-step assignment creation
        - Rubric templates
        - Auto-generate test cases
        - Import from existing assignments
        """)
    
    @staticmethod
    def show_course_planning_helper():
        """Display the course planning helper"""
        st.subheader("📅 Course Planning Helper")
        st.info("This feature helps you plan your course assignments and grading schedule.")
        
        st.markdown("""
        **Coming Soon:**
        - Semester planning
        - Assignment scheduling
        - Workload estimation
        - Grading timeline
        """)
