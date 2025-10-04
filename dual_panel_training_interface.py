#!/usr/bin/env python3
"""
Dual Panel Training Interface
Two independently scrollable panels for submission list and review
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import os
import nbformat
from datetime import datetime
from typing import Dict, List, Any, Optional

class DualPanelTrainingInterface:
    """Training interface with dual independently scrollable panels"""
    
    def __init__(self, db_path: str = "grading_database.db"):
        self.db_path = db_path
        
    def render(self):
        """Render the dual panel training interface"""
        
        st.title("🎓 AI Training Review")
        
        # Add custom CSS for fixed height scrollable panels matching reference image
        st.markdown("""
            <style>
            /* Remove default padding */
            .main .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                max-width: 100%;
            }
            
            /* Hide streamlit default elements */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            
            /* Fixed height containers for independent scrolling */
            div[data-testid="stVerticalBlock"] > div:has(div.scrollable-left) {
                height: calc(100vh - 180px);
                overflow-y: auto;
                overflow-x: hidden;
            }
            
            div[data-testid="stVerticalBlock"] > div:has(div.scrollable-right) {
                height: calc(100vh - 180px);
                overflow-y: auto;
                overflow-x: hidden;
            }
            
            /* Custom scrollbar styling */
            ::-webkit-scrollbar {
                width: 10px;
            }
            
            ::-webkit-scrollbar-track {
                background: #0e1117;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #31333f;
                border-radius: 5px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: #40424e;
            }
            
            /* Submission list styling */
            .stButton button {
                width: 100%;
                text-align: left;
                background-color: #262730;
                border: none;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 4px;
                color: white;
                font-size: 14px;
                transition: all 0.2s;
            }
            
            .stButton button:hover {
                background-color: #31333f;
                border-left: 3px solid #4a9eff;
            }
            
            /* Selected submission highlight */
            .stButton button[kind="primary"] {
                background-color: #ff4b4b !important;
                border-left: 3px solid #ff4b4b;
            }
            
            /* Compact metrics */
            div[data-testid="stMetricValue"] {
                font-size: 24px;
            }
            
            /* Section headers */
            .section-title {
                font-size: 18px;
                font-weight: 600;
                color: #fafafa;
                margin-bottom: 12px;
                padding-bottom: 8px;
                border-bottom: 1px solid #31333f;
            }
            
            /* Expander styling */
            .streamlit-expanderHeader {
                background-color: #262730;
                border-radius: 4px;
                font-size: 14px;
            }
            
            /* Tab styling */
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                background-color: #262730;
                border-radius: 4px 4px 0 0;
                padding: 8px 16px;
            }
            
            .stTabs [aria-selected="true"] {
                background-color: #31333f;
            }
            
            /* Info boxes */
            .stAlert {
                padding: 8px 12px;
                font-size: 13px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Top filters row
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            assignment_filter = st.selectbox(
                "📚 Assignment",
                self._get_assignments(),
                key="assignment_filter"
            )
        
        with col2:
            status_filter = st.selectbox(
                "📊 Review Status",
                ["All", "Needs Review", "Human Reviewed", "AI Only"],
                key="status_filter"
            )
        
        with col3:
            score_filter = st.selectbox(
                "🎯 Filter by Score",
                ["All", "Excellent (>90%)", "Good (80-90%)", "Fair (70-80%)", "Poor (<70%)"],
                key="score_filter"
            )
        
        # Create two columns for the dual panel layout
        left_col, right_col = st.columns([1, 2])
        
        # LEFT PANEL: Submission List
        with left_col:
            st.markdown("### 📋 Submissions")
            
            # Get filtered submissions
            submissions = self._get_filtered_submissions(
                assignment_filter,
                status_filter,
                score_filter
            )
            
            st.markdown(f"*Showing {len(submissions)} submissions*")
            
            # Render submission list in scrollable container
            self._render_submission_list(submissions)
        
        # RIGHT PANEL: Review Details
        with right_col:
            if 'selected_submission_id' in st.session_state and st.session_state.selected_submission_id:
                self._render_review_panel(st.session_state.selected_submission_id)
            else:
                st.info("👈 Select a submission from the list to review")
    
    def _get_assignments(self) -> List[str]:
        """Get list of assignments"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT a.name
                FROM assignments a
                INNER JOIN submissions s ON a.id = s.assignment_id
                ORDER BY a.name
            """)
            
            assignments = ["All"] + [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return assignments
            
        except Exception as e:
            st.error(f"Error loading assignments: {e}")
            return ["All"]
    
    def _get_filtered_submissions(self, assignment: str, status: str, score: str) -> List[Dict]:
        """Get filtered submissions based on criteria"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = """
                SELECT 
                    s.id,
                    s.student_id,
                    s.assignment_id,
                    a.name as assignment_name,
                    s.ai_score,
                    s.human_score,
                    s.final_score,
                    s.human_feedback,
                    s.graded_date,
                    CASE 
                        WHEN s.human_score IS NOT NULL THEN 'Human Reviewed'
                        WHEN s.ai_score IS NOT NULL THEN 'AI Only'
                        ELSE 'Needs Review'
                    END as review_status
                FROM submissions s
                INNER JOIN assignments a ON s.assignment_id = a.id
                WHERE 1=1
            """
            
            params = []
            
            # Assignment filter
            if assignment != "All":
                query += " AND a.name = ?"
                params.append(assignment)
            
            # Status filter
            if status == "Needs Review":
                query += " AND s.human_score IS NULL AND s.ai_score IS NULL"
            elif status == "Human Reviewed":
                query += " AND s.human_score IS NOT NULL"
            elif status == "AI Only":
                query += " AND s.ai_score IS NOT NULL AND s.human_score IS NULL"
            
            # Score filter
            if score == "Excellent (>90%)":
                query += " AND COALESCE(s.final_score, s.ai_score, 0) > 90"
            elif score == "Good (80-90%)":
                query += " AND COALESCE(s.final_score, s.ai_score, 0) BETWEEN 80 AND 90"
            elif score == "Fair (70-80%)":
                query += " AND COALESCE(s.final_score, s.ai_score, 0) BETWEEN 70 AND 80"
            elif score == "Poor (<70%)":
                query += " AND COALESCE(s.final_score, s.ai_score, 0) < 70"
            
            query += " ORDER BY s.graded_date DESC, s.student_id"
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            st.error(f"Error loading submissions: {e}")
            return []
    
    def _render_submission_list(self, submissions: List[Dict]):
        """Render the scrollable submission list"""
        
        # Use container with fixed height for scrolling
        with st.container():
            for submission in submissions:
                self._render_submission_card(submission)
    
    def _render_submission_card(self, submission: Dict):
        """Render a single submission card"""
        
        # Determine score and label
        score = submission.get('final_score') or submission.get('ai_score') or 0
        
        if score >= 90:
            score_label = "Excellent"
            score_color = "🟢"
        elif score >= 80:
            score_label = "Good"
            score_color = "🟡"
        elif score >= 70:
            score_label = "Fair"
            score_color = "🟠"
        else:
            score_label = "Poor"
            score_color = "🔴"
        
        # Check if selected
        is_selected = ('selected_submission_id' in st.session_state and 
                      st.session_state.selected_submission_id == submission['id'])
        
        # Create clickable button with styling
        button_type = "primary" if is_selected else "secondary"
        
        if st.button(
            f"{score_color} {submission['student_id']} - {score:.1f}%",
            key=f"sub_{submission['id']}",
            use_container_width=True,
            type=button_type
        ):
            st.session_state.selected_submission_id = submission['id']
            st.rerun()
        
        # Display status
        col1, col2 = st.columns([1, 1])
        with col1:
            st.caption(f"{score_label}")
        with col2:
            if submission.get('human_score') is not None:
                st.caption("✅ Human reviewed")
            else:
                st.caption("🤖 AI only")
        
        st.divider()
    
    def _render_review_panel(self, submission_id: int):
        """Render the review panel for selected submission"""
        
        # Get submission details
        submission = self._get_submission_details(submission_id)
        
        if not submission:
            st.error("Submission not found")
            return
        
        # Header
        st.markdown(f"### 📝 Review: {submission['student_id']}")
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 AI Feedback", "📓 Notebook", "✍️ Human Review"])
        
        with tab1:
            self._render_ai_feedback_tab(submission)
        
        with tab2:
            self._render_notebook_tab(submission)
        
        with tab3:
            self._render_human_review_tab(submission)
    
    def _get_submission_details(self, submission_id: int) -> Optional[Dict]:
        """Get detailed submission information"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = """
                SELECT 
                    s.*,
                    a.name as assignment_name,
                    a.total_points as max_score
                FROM submissions s
                INNER JOIN assignments a ON s.assignment_id = a.id
                WHERE s.id = ?
            """
            
            df = pd.read_sql_query(query, conn, params=(submission_id,))
            conn.close()
            
            if len(df) == 0:
                return None
            
            return df.iloc[0].to_dict()
            
        except Exception as e:
            st.error(f"Error loading submission: {e}")
            return None
    
    def _render_ai_feedback_tab(self, submission: Dict):
        """Render AI feedback tab"""
        
        st.markdown('<div class="review-section">', unsafe_allow_html=True)
        
        # Overall Assessment
        st.markdown('<div class="section-header">📊 Overall Assessment</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("AI Score", f"{submission.get('ai_score', 0):.1f}")
        with col2:
            st.metric("Human Score", f"{submission.get('human_score', 'N/A')}")
        with col3:
            st.metric("Final Score", f"{submission.get('final_score', 0):.1f}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Parse and display AI feedback
        if submission.get('ai_feedback'):
            try:
                feedback = json.loads(submission['ai_feedback'])
                
                # Comprehensive Feedback
                if 'comprehensive_feedback' in feedback:
                    comp_feedback = feedback['comprehensive_feedback']
                    
                    # Instructor Comments
                    if isinstance(comp_feedback, dict) and 'instructor_comments' in comp_feedback:
                        st.markdown('<div class="review-section">', unsafe_allow_html=True)
                        st.markdown('<div class="section-header">💬 Instructor Comments</div>', unsafe_allow_html=True)
                        st.write(comp_feedback['instructor_comments'])
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Detailed Feedback Sections
                    if isinstance(comp_feedback, dict) and 'detailed_feedback' in comp_feedback:
                        detailed = comp_feedback['detailed_feedback']
                        
                        sections = {
                            'reflection_assessment': '🤔 Reflection & Critical Thinking',
                            'analytical_strengths': '💪 Analytical Strengths',
                            'business_application': '💼 Business Application',
                            'learning_demonstration': '📚 Learning Demonstration',
                            'areas_for_development': '🎯 Areas for Development',
                            'recommendations': '💡 Recommendations'
                        }
                        
                        for key, title in sections.items():
                            if key in detailed and detailed[key]:
                                with st.expander(title, expanded=False):
                                    for item in detailed[key]:
                                        st.markdown(f"• {item}")
            
            except json.JSONDecodeError:
                st.warning("Could not parse AI feedback")
                st.text(submission['ai_feedback'])
        else:
            st.info("No AI feedback available")
    
    def _render_notebook_tab(self, submission: Dict):
        """Render notebook preview tab"""
        
        st.markdown('<div class="review-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📓 Notebook Preview</div>', unsafe_allow_html=True)
        
        notebook_path = submission.get('notebook_path')
        
        if notebook_path and os.path.exists(notebook_path):
            try:
                with open(notebook_path, 'r') as f:
                    nb = nbformat.read(f, as_version=4)
                
                st.info(f"Notebook: {os.path.basename(notebook_path)}")
                st.info(f"Cells: {len(nb.cells)}")
                
                # Show first few cells
                with st.expander("Preview First 5 Cells", expanded=True):
                    for i, cell in enumerate(nb.cells[:5]):
                        st.markdown(f"**Cell {i+1} ({cell.cell_type})**")
                        if cell.cell_type == 'code':
                            st.code(cell.source, language='python')
                        else:
                            st.markdown(cell.source)
                        st.markdown("---")
                
            except Exception as e:
                st.error(f"Error loading notebook: {e}")
        else:
            st.warning("Notebook file not found")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_human_review_tab(self, submission: Dict):
        """Render human review tab"""
        
        st.markdown('<div class="review-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">✍️ Human Review</div>', unsafe_allow_html=True)
        
        # Show existing human feedback if available
        if submission.get('human_feedback'):
            st.markdown("**Current Human Feedback:**")
            st.info(submission['human_feedback'])
        
        # Human review form
        st.markdown("---")
        st.markdown("**Add/Update Human Review:**")
        
        human_score = st.number_input(
            "Human Score",
            min_value=0.0,
            max_value=float(submission.get('max_score', 100)),
            value=float(submission.get('human_score', submission.get('ai_score', 0))),
            step=0.5,
            key=f"human_score_{submission['id']}"
        )
        
        human_feedback = st.text_area(
            "Human Feedback",
            value=submission.get('human_feedback', ''),
            height=200,
            key=f"human_feedback_{submission['id']}"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save Review", use_container_width=True):
                self._save_human_review(submission['id'], human_score, human_feedback)
                st.success("Review saved!")
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset to AI Score", use_container_width=True):
                self._reset_to_ai_score(submission['id'])
                st.success("Reset to AI score!")
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _save_human_review(self, submission_id: int, human_score: float, human_feedback: str):
        """Save human review to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE submissions
                SET human_score = ?,
                    human_feedback = ?,
                    final_score = ?,
                    graded_date = ?
                WHERE id = ?
            """, (human_score, human_feedback, human_score, datetime.now(), submission_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error saving review: {e}")
    
    def _reset_to_ai_score(self, submission_id: int):
        """Reset submission to AI score"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE submissions
                SET human_score = NULL,
                    human_feedback = NULL,
                    final_score = ai_score
                WHERE id = ?
            """, (submission_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error resetting score: {e}")


def render_dual_panel_training_interface():
    """Main function to render the dual panel training interface"""
    
    # Initialize session state
    if 'selected_submission_id' not in st.session_state:
        st.session_state.selected_submission_id = None
    
    # Create and render interface
    interface = DualPanelTrainingInterface()
    interface.render()


if __name__ == "__main__":
    st.set_page_config(
        page_title="AI Training Review",
        page_icon="🎓",
        layout="wide"
    )
    
    render_dual_panel_training_interface()
