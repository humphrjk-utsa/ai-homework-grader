#!/usr/bin/env python3
"""
Enhanced Training Integration
Integrates the enhanced training interface with the main Streamlit application
"""

import streamlit as st
from enhanced_training_page import enhanced_training_page

def integrate_enhanced_training():
    """
    Integration function to add enhanced training to main app
    
    Add this to your main app.py navigation:
    
    ```python
    from enhanced_training_integration import integrate_enhanced_training
    
    # In your page selection logic:
    elif page == "Enhanced AI Training":
        integrate_enhanced_training()
    ```
    """
    
    try:
        enhanced_training_page()
    except Exception as e:
        st.error(f"Error loading enhanced training interface: {e}")
        st.info("Please ensure all dependencies are installed and the database is properly configured.")

def add_to_sidebar():
    """
    Add enhanced training option to sidebar navigation
    
    Call this function in your main app to add the navigation option:
    
    ```python
    from enhanced_training_integration import add_to_sidebar
    
    # In your sidebar setup:
    add_to_sidebar()
    ```
    """
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎓 Enhanced Training")
    
    if st.sidebar.button("📊 Enhanced AI Training Review"):
        st.session_state.page = "Enhanced AI Training"

# Example integration for app.py
INTEGRATION_EXAMPLE = """
# Add this to your main app.py file:

import streamlit as st
from enhanced_training_integration import integrate_enhanced_training, add_to_sidebar

def main():
    st.set_page_config(page_title="Grading System", layout="wide")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Your existing navigation options
    page = st.sidebar.selectbox("Choose a page", [
        "Home",
        "Grade Assignments", 
        "Training Interface",
        "Enhanced AI Training",  # Add this option
        "Reports"
    ])
    
    # Add enhanced training sidebar button
    add_to_sidebar()
    
    # Page routing
    if page == "Home":
        show_home_page()
    elif page == "Grade Assignments":
        show_grading_page()
    elif page == "Training Interface":
        show_training_page()
    elif page == "Enhanced AI Training":
        integrate_enhanced_training()  # Add this
    elif page == "Reports":
        show_reports_page()
    
    # Handle sidebar button navigation
    if st.session_state.get('page') == "Enhanced AI Training":
        integrate_enhanced_training()

if __name__ == "__main__":
    main()
"""

def show_integration_guide():
    """Show integration guide for developers"""
    st.title("🔧 Enhanced Training Integration Guide")
    
    st.markdown("""
    ## Quick Integration Steps
    
    1. **Import the integration module** in your main app.py:
    ```python
    from enhanced_training_integration import integrate_enhanced_training, add_to_sidebar
    ```
    
    2. **Add to your page selection logic**:
    ```python
    elif page == "Enhanced AI Training":
        integrate_enhanced_training()
    ```
    
    3. **Add sidebar navigation** (optional):
    ```python
    add_to_sidebar()
    ```
    
    ## Complete Example
    """)
    
    st.code(INTEGRATION_EXAMPLE, language="python")
    
    st.markdown("""
    ## Database Setup
    
    The enhanced training interface will automatically set up the required database tables
    when first loaded. Make sure your existing `grading_database.db` is accessible.
    
    ## Dependencies
    
    Ensure these packages are installed:
    - streamlit
    - pandas
    - sqlite3 (built-in)
    - nbformat
    - json (built-in)
    
    ## Troubleshooting
    
    If you encounter issues:
    1. Check that the database file exists and is writable
    2. Verify all Python dependencies are installed
    3. Check the logs in the `logs/` directory for detailed error information
    4. Ensure notebook files exist at the paths stored in the database
    """)

if __name__ == "__main__":
    show_integration_guide()