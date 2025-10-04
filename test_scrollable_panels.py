#!/usr/bin/env python3
"""
Test Scrollable Panels
Simple test to verify the independent scrollable areas work correctly
"""

import streamlit as st
from dual_panel_layout import DualPanelLayout

def test_scrollable_layout():
    """Test the scrollable dual panel layout"""
    
    st.title("🧪 Scrollable Dual Panel Test")
    st.markdown("Testing independent scrollable areas for left and right panels")
    
    # Initialize layout
    layout = DualPanelLayout()
    
    def render_left_header():
        st.markdown("### 📋 Left Panel Header")
        st.caption("This header stays fixed while content below scrolls")
    
    def render_left_content():
        st.markdown("**Scrollable Content Area**")
        
        # Generate lots of content to test scrolling
        for i in range(50):
            with st.container():
                st.markdown(f"""
                <div style="background: white; border: 1px solid #ddd; border-radius: 4px; 
                           padding: 0.5rem; margin-bottom: 0.5rem;">
                    <strong>Item {i+1}</strong><br>
                    This is scrollable content item {i+1}. The left panel should scroll independently.
                </div>
                """, unsafe_allow_html=True)
    
    def render_right_header():
        st.markdown("### 👤 Right Panel Header")
        st.caption("Selected item details appear here - header stays fixed")
    
    def render_right_content():
        st.markdown("**Detailed View Content**")
        
        # Simulate detailed content
        tabs = st.tabs(["📊 Details", "📓 Content", "✏️ Review"])
        
        with tabs[0]:
            st.markdown("#### Details Tab")
            for i in range(30):
                st.write(f"Detail line {i+1}: This content should scroll independently from the left panel.")
        
        with tabs[1]:
            st.markdown("#### Content Tab")
            st.code("""
# Sample code content
def example_function():
    print("This is sample code content")
    for i in range(100):
        print(f"Line {i}")
    return "Done"
            """, language="python")
        
        with tabs[2]:
            st.markdown("#### Review Tab")
            st.text_area("Review Comments", height=200)
            st.slider("Score", 0, 100, 85)
    
    # Create the layout
    layout.create_layout(
        render_left_header,
        render_left_content,
        render_right_header,
        render_right_content
    )
    
    st.markdown("---")
    st.markdown("""
    **Test Instructions:**
    1. The left panel should have its own scroll bar and scroll independently
    2. The right panel should have its own scroll bar and scroll independently  
    3. Headers should stay fixed while content scrolls
    4. On mobile, panels should stack vertically
    """)

if __name__ == "__main__":
    test_scrollable_layout()