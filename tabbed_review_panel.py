#!/usr/bin/env python3
"""
Tabbed Review Panel
Right panel interface with tabs for AI Feedback, Notebook, and Human Review
"""

import streamlit as st
import json
import nbformat
from typing import Dict, List, Any, Optional, Callable
from dual_panel_layout import DualPanelLayout

class TabbedReviewPanel:
    """Manages the right panel tabbed interface for detailed submission review"""
    
    def __init__(self, layout: DualPanelLayout):
        self.layout = layout
        self.setup_panel_css()
    
    def setup_panel_css(self):
        """Set up CSS specific to the tabbed review panel"""
        
        st.markdown("""
        <style>
        /* Tab container styling - fits within right panel scroll area */
        .review-panel-container {
            height: 100%;
            overflow: visible; /* Let parent handle scrolling */
        }
        
        /* Enhanced tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background-color: #f8f9fa;
            padding: 0.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            padding: 0 24px;
            background-color: white;
            border-radius: 8px;
            border: 2px solid #e9ecef;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            border-color: #007bff;
            background-color: #f8f9ff;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #007bff;
            color: white;
            border-color: #007bff;
            box-shadow: 0 4px 12px rgba(0,123,255,0.3);
        }
        
        /* Tab content styling */
        .tab-content {
            background-color: white;
            border-radius: 8px;
            padding: 1.5rem;
            border: 1px solid #e9ecef;
            min-height: 400px;
        }
        
        /* AI Feedback specific styling */
        .ai-feedback-container {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .feedback-section {
            background: white;
            border-radius: 6px;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 4px solid #007bff;
        }
        
        .feedback-section h4 {
            color: #2c3e50;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .feedback-item {
            background-color: #f8f9fa;
            border-radius: 4px;
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-left: 3px solid #28a745;
        }
        
        .feedback-item:last-child {
            margin-bottom: 0;
        }
        
        /* Score metrics styling */
        .score-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .score-metric {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }
        
        .score-metric-value {
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 0.25rem;
        }
        
        .score-metric-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        /* Notebook viewer styling */
        .notebook-container {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 1rem;
        }
        
        .notebook-cell {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            margin-bottom: 1rem;
            overflow: hidden;
        }
        
        .cell-header {
            background-color: #f8f9fa;
            padding: 0.5rem 1rem;
            border-bottom: 1px solid #e9ecef;
            font-size: 0.9em;
            color: #6c757d;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .cell-content {
            padding: 1rem;
        }
        
        .cell-output {
            background-color: #f8f9fa;
            border-top: 1px solid #e9ecef;
            padding: 1rem;
        }
        
        .cell-error {
            background-color: #f8d7da;
            color: #721c24;
            border-top: 1px solid #f5c6cb;
            padding: 1rem;
        }
        
        /* Human review form styling */
        .human-review-container {
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            border-radius: 8px;
            padding: 1.5rem;
        }
        
        .review-form {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 1.5rem;
        }
        
        .form-section {
            margin-bottom: 1.5rem;
        }
        
        .form-section h4 {
            color: #2c3e50;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e9ecef;
        }
        
        .template-button {
            background-color: #e9ecef;
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            margin: 0.25rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .template-button:hover {
            background-color: #007bff;
            color: white;
            border-color: #007bff;
        }
        
        .action-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 1.5rem;
        }
        
        .primary-button {
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .primary-button:hover {
            background-color: #0056b3;
            transform: translateY(-1px);
        }
        
        .secondary-button {
            background-color: #6c757d;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .secondary-button:hover {
            background-color: #545b62;
            transform: translateY(-1px);
        }
        
        /* View mode selector */
        .view-mode-selector {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .view-mode-buttons {
            display: flex;
            gap: 0.5rem;
        }
        
        .view-mode-button {
            padding: 0.5rem 1rem;
            border: 1px solid #ced4da;
            border-radius: 4px;
            background: white;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .view-mode-button.active {
            background-color: #007bff;
            color: white;
            border-color: #007bff;
        }
        
        /* Loading states */
        .loading-content {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
            color: #6c757d;
        }
        
        .error-content {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            border-radius: 6px;
            padding: 1rem;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_tabbed_interface(self, submission: Dict[str, Any], 
                              training_interface: Any) -> Dict[str, Any]:
        """
        Render the complete tabbed interface for submission review
        
        Args:
            submission: Selected submission data
            training_interface: Training interface instance for data operations
            
        Returns:
            Dict with any actions that occurred
        """
        
        actions = {}
        
        # Create tabs (header will be rendered separately)
        tab1, tab2, tab3 = st.tabs(["📊 AI Feedback", "📓 Notebook", "✏️ Human Review"])
        
        with tab1:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            ai_actions = self._render_ai_feedback_tab(submission)
            if ai_actions:
                actions.update(ai_actions)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            notebook_actions = self._render_notebook_tab(submission, training_interface)
            if notebook_actions:
                actions.update(notebook_actions)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            review_actions = self._render_human_review_tab(submission, training_interface)
            if review_actions:
                actions.update(review_actions)
            st.markdown('</div>', unsafe_allow_html=True)
        
        return actions
    
    def render_submission_header(self, submission: Dict[str, Any]):
        """Render header with submission information - this goes in the right panel header"""
        
        max_score = submission.get('max_score', 37.5)
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 1rem; border-radius: 6px; margin: -1rem -1rem 0 -1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; margin-bottom: 0.25rem;">
                        👤 {submission['student_name']}
                    </h3>
                    <div style="font-size: 0.9em; opacity: 0.9;">
                        <strong>ID:</strong> {submission.get('student_id', 'N/A')} | 
                        <strong>Submitted:</strong> {submission.get('submission_date', 'Unknown')}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.8em; font-weight: bold;">
                        {submission['final_score']:.1f}/{max_score:.1f}
                    </div>
                    <div style="font-size: 0.8em; opacity: 0.9;">
                        {submission['score_status']}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_ai_feedback_tab(self, submission: Dict[str, Any]) -> Optional[Dict]:
        """Render AI feedback tab content"""
        
        st.markdown("### 🤖 AI-Generated Feedback")
        
        # Score metrics
        self._render_score_metrics(submission)
        
        # Parse and display AI feedback
        ai_feedback = submission.get('ai_feedback')
        if not ai_feedback:
            st.info("No AI feedback available for this submission.")
            return None
        
        try:
            # Try to parse as JSON
            if isinstance(ai_feedback, str):
                feedback_data = json.loads(ai_feedback)
            else:
                feedback_data = ai_feedback
            
            # Display structured feedback
            if isinstance(feedback_data, dict):
                self._render_structured_feedback(feedback_data)
            else:
                # Fallback for non-structured feedback
                st.text_area("AI Feedback", str(feedback_data), height=300, disabled=True)
        
        except json.JSONDecodeError:
            # Fallback for non-JSON feedback
            st.subheader("Raw AI Feedback")
            st.text_area("Feedback Content", ai_feedback, height=300, disabled=True)
        
        except Exception as e:
            st.error(f"Error displaying AI feedback: {e}")
        
        return None
    
    def _render_score_metrics(self, submission: Dict[str, Any]):
        """Render score metrics section"""
        
        ai_score = submission.get('ai_score', 0)
        human_score = submission.get('human_score')
        final_score = submission.get('final_score', 0)
        max_score = submission.get('max_score', 37.5)
        
        st.markdown(f"""
        <div class="score-metrics">
            <div class="score-metric">
                <div class="score-metric-value">{ai_score:.1f}/{max_score:.1f}</div>
                <div class="score-metric-label">AI Score</div>
            </div>
            <div class="score-metric">
                <div class="score-metric-value">{human_score:.1f if human_score else 'N/A'}/{max_score:.1f}</div>
                <div class="score-metric-label">Human Score</div>
            </div>
            <div class="score-metric">
                <div class="score-metric-value">{final_score:.1f}/{max_score:.1f}</div>
                <div class="score-metric-label">Final Score</div>
            </div>
            <div class="score-metric">
                <div class="score-metric-value">{(final_score/max_score*100):.1f}%</div>
                <div class="score-metric-label">Percentage</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_structured_feedback(self, feedback_data: Dict[str, Any]):
        """Render structured AI feedback"""
        
        # Instructor comments (if available)
        if 'instructor_comments' in feedback_data:
            st.markdown(f"""
            <div class="feedback-section">
                <h4>💬 Overall Assessment</h4>
                <div class="feedback-item">
                    {feedback_data['instructor_comments']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Detailed feedback sections
        if 'detailed_feedback' in feedback_data:
            detailed = feedback_data['detailed_feedback']
            
            feedback_sections = [
                ('🤔 Reflection Assessment', 'reflection_assessment'),
                ('💪 Analytical Strengths', 'analytical_strengths'),
                ('🏢 Business Application', 'business_application'),
                ('📈 Learning Demonstration', 'learning_demonstration'),
                ('🔧 Areas for Development', 'areas_for_development'),
                ('💡 Recommendations', 'recommendations')
            ]
            
            for title, key in feedback_sections:
                if key in detailed and detailed[key]:
                    with st.expander(title, expanded=(key == 'reflection_assessment')):
                        for item in detailed[key]:
                            st.markdown(f"""
                            <div class="feedback-item">
                                • {item}
                            </div>
                            """, unsafe_allow_html=True)
        
        # Component scores (if available)
        if 'component_scores' in feedback_data:
            st.subheader("📊 Component Breakdown")
            components = feedback_data['component_scores']
            
            cols = st.columns(len(components))
            for i, (component, score) in enumerate(components.items()):
                with cols[i]:
                    st.metric(component.replace('_', ' ').title(), f"{score:.1f}")
    
    def _render_notebook_tab(self, submission: Dict[str, Any], 
                           training_interface: Any) -> Optional[Dict]:
        """Render notebook viewer tab content"""
        
        st.markdown("### 📓 Student Notebook")
        
        # View mode selector
        view_mode = st.radio(
            "View Mode",
            ["Full Interactive", "Code Only", "Summary"],
            horizontal=True,
            key=f"notebook_view_{submission['id']}"
        )
        
        # Load notebook content
        notebook_path = submission.get('notebook_path')
        if not notebook_path:
            st.warning("No notebook file associated with this submission.")
            return None
        
        try:
            notebook_content = training_interface.get_notebook_content(notebook_path)
            if not notebook_content:
                st.error(f"Could not load notebook: {notebook_path}")
                return None
            
            # Display notebook based on view mode
            if view_mode == "Summary":
                self._render_notebook_summary(notebook_content)
            elif view_mode == "Code Only":
                self._render_notebook_code_only(notebook_content)
            else:  # Full Interactive
                self._render_notebook_full(notebook_content)
        
        except Exception as e:
            st.error(f"Error loading notebook: {e}")
            st.info(f"Notebook path: {notebook_path}")
        
        return None
    
    def _render_notebook_summary(self, notebook_content: Dict[str, Any]):
        """Render notebook summary view"""
        
        notebook = notebook_content['notebook']
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Cells", notebook_content['cell_count'])
        with col2:
            st.metric("Code Cells", notebook_content['code_cells'])
        with col3:
            st.metric("Markdown Cells", notebook_content['markdown_cells'])
        with col4:
            st.metric("Has Outputs", "Yes" if notebook_content.get('has_outputs') else "No")
        
        # First few cells preview
        st.subheader("📋 Notebook Preview")
        for i, cell in enumerate(notebook.cells[:5]):
            with st.expander(f"Cell {i+1} ({cell.cell_type})", expanded=False):
                if cell.cell_type == 'code':
                    st.code(cell.source, language='python')
                elif cell.cell_type == 'markdown':
                    st.markdown(cell.source)
        
        if len(notebook.cells) > 5:
            st.info(f"... and {len(notebook.cells) - 5} more cells")
    
    def _render_notebook_code_only(self, notebook_content: Dict[str, Any]):
        """Render notebook code-only view"""
        
        notebook = notebook_content['notebook']
        code_cells = [cell for cell in notebook.cells if cell.cell_type == 'code']
        
        if not code_cells:
            st.info("No code cells found in this notebook.")
            return
        
        for i, cell in enumerate(code_cells):
            st.markdown(f"**Code Cell {i+1}**")
            st.code(cell.source, language='python')
            
            # Show outputs if available
            if hasattr(cell, 'outputs') and cell.outputs:
                with st.expander("Output", expanded=False):
                    for output in cell.outputs:
                        if output.output_type == 'stream':
                            st.text(output.text)
                        elif output.output_type == 'execute_result':
                            if 'text/plain' in output.data:
                                st.text(output.data['text/plain'])
                        elif output.output_type == 'error':
                            st.error(f"Error: {output.ename}: {output.evalue}")
    
    def _render_notebook_full(self, notebook_content: Dict[str, Any]):
        """Render full interactive notebook view"""
        
        notebook = notebook_content['notebook']
        
        st.markdown('<div class="notebook-container">', unsafe_allow_html=True)
        
        for i, cell in enumerate(notebook.cells):
            st.markdown(f"""
            <div class="notebook-cell">
                <div class="cell-header">
                    <span>Cell {i+1} ({cell.cell_type})</span>
                    <span>{'Executed' if hasattr(cell, 'execution_count') and cell.execution_count else 'Not executed'}</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Cell content
            st.markdown('<div class="cell-content">', unsafe_allow_html=True)
            if cell.cell_type == 'code':
                st.code(cell.source, language='python')
            elif cell.cell_type == 'markdown':
                st.markdown(cell.source)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Cell outputs
            if hasattr(cell, 'outputs') and cell.outputs:
                for output in cell.outputs:
                    if output.output_type == 'stream':
                        st.markdown('<div class="cell-output">', unsafe_allow_html=True)
                        st.text(output.text)
                        st.markdown('</div>', unsafe_allow_html=True)
                    elif output.output_type == 'execute_result':
                        st.markdown('<div class="cell-output">', unsafe_allow_html=True)
                        if 'text/html' in output.data:
                            st.markdown(output.data['text/html'], unsafe_allow_html=True)
                        elif 'text/plain' in output.data:
                            st.text(output.data['text/plain'])
                        st.markdown('</div>', unsafe_allow_html=True)
                    elif output.output_type == 'error':
                        st.markdown('<div class="cell-error">', unsafe_allow_html=True)
                        st.error(f"Error: {output.ename}: {output.evalue}")
                        if hasattr(output, 'traceback'):
                            st.code('\n'.join(output.traceback))
                        st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_human_review_tab(self, submission: Dict[str, Any], 
                               training_interface: Any) -> Optional[Dict]:
        """Render human review tab content"""
        
        st.markdown("### ✏️ Human Review & Feedback")
        
        # Get existing human feedback
        existing_feedback = training_interface.get_human_feedback(submission['id'])
        
        # Review form
        with st.form(f"human_review_{submission['id']}"):
            st.markdown('<div class="human-review-container">', unsafe_allow_html=True)
            
            # Score section
            st.markdown("#### 📊 Score Assessment")
            col1, col2 = st.columns(2)
            
            max_score = submission.get('max_score', 37.5)
            
            with col1:
                human_score = st.number_input(
                    f"Human Score (0-{max_score:.1f})",
                    min_value=0.0,
                    max_value=float(max_score),
                    value=float(existing_feedback['score'] if existing_feedback else submission['ai_score']),
                    step=0.5,
                    help="Enter your assessment of this submission"
                )
            
            with col2:
                score_difference = human_score - submission['ai_score']
                st.metric(
                    "Difference from AI", 
                    f"{score_difference:+.1f}",
                    delta=f"{score_difference:+.1f} points"
                )
            
            # Feedback templates
            st.markdown("#### 📝 Feedback Templates")
            template_options = [
                "Custom",
                "Excellent work! Shows strong understanding and complete execution of all requirements.",
                "Good effort with solid fundamentals. Some areas for improvement have been identified.",
                "Satisfactory work that meets basic requirements but could benefit from more depth.",
                "Needs significant improvement - missing key components or contains major errors.",
                "Incomplete submission - please address the missing sections and resubmit."
            ]
            
            selected_template = st.selectbox(
                "Quick Templates",
                template_options,
                help="Select a template to start with, then customize as needed"
            )
            
            # Feedback text area
            if existing_feedback and selected_template == "Custom":
                default_feedback = existing_feedback['feedback']
            elif selected_template != "Custom":
                default_feedback = selected_template
            else:
                default_feedback = ""
            
            human_feedback_text = st.text_area(
                "Detailed Feedback",
                value=default_feedback,
                height=200,
                help="Provide detailed feedback to help the student improve"
            )
            
            # Character count
            char_count = len(human_feedback_text)
            st.caption(f"Characters: {char_count} (recommended: 100-500)")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Action buttons
            st.markdown("#### 🎯 Actions")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                save_review = st.form_submit_button(
                    "💾 Save Review", 
                    type="primary",
                    use_container_width=True
                )
            
            with col2:
                generate_pdf = st.form_submit_button(
                    "📄 Generate PDF",
                    use_container_width=True
                )
            
            with col3:
                approve_ai = st.form_submit_button(
                    "✅ Approve AI Grade",
                    use_container_width=True
                )
            
            with col4:
                next_student = st.form_submit_button(
                    "➡️ Next Student",
                    use_container_width=True
                )
            
            # Handle form submissions
            if save_review:
                if training_interface.save_human_feedback(submission['id'], human_score, human_feedback_text):
                    st.success("✅ Human review saved successfully!")
                    return {'action': 'save_review', 'score': human_score, 'feedback': human_feedback_text}
                else:
                    st.error("❌ Failed to save review")
            
            if generate_pdf:
                return {
                    'action': 'generate_clean_pdf', 
                    'submission_id': submission['id'],
                    'student_name': submission['student_name']
                }
            
            if approve_ai:
                ai_score = submission['ai_score']
                if training_interface.save_human_feedback(submission['id'], ai_score, "AI grade approved by instructor"):
                    st.success("✅ AI grade approved!")
                    return {'action': 'approve_ai', 'score': ai_score}
                else:
                    st.error("❌ Failed to approve AI grade")
            
            if next_student:
                return {'action': 'next_student'}
        
        # Show existing review information
        if existing_feedback:
            st.info(f"📅 Last updated: {existing_feedback['last_updated']} by {existing_feedback['instructor_id']}")
        
        return None