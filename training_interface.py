import streamlit as st
import sqlite3
import pandas as pd
import json
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from ai_grader import AIGrader
from correction_helpers import CorrectionHelpers
from assignment_setup_helper import AssignmentSetupHelper
from alternative_approaches import AlternativeApproachHandler

class TrainingInterface:
    """Interface for training the AI model to grade more like the instructor"""
    
    def __init__(self, grader):
        self.grader = grader
        self.ai_grader = AIGrader(grader)
    
    def show_training_dashboard(self):
        """Main training dashboard"""
        st.title("🎯 AI Training Dashboard")
        st.markdown("Train the AI to grade more like you by reviewing and correcting its assessments.")
        
        # Training statistics
        self.show_training_stats()
        
        # Training workflow tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📝 Review & Correct", 
            "📊 Training Progress", 
            "🔄 Retrain Model", 
            "📈 Performance Analytics",
            "🧙‍♂️ Setup Helper",
            "🔄 Alternative Approaches"
        ])
        
        with tab1:
            self.show_correction_interface()
        
        with tab2:
            self.show_training_progress()
        
        with tab3:
            self.show_retraining_interface()
        
        with tab4:
            self.show_performance_analytics()
        
        with tab5:
            self.show_setup_helper()
        
        with tab6:
            self.show_alternative_approaches()
    
    def show_training_stats(self):
        """Display current training statistics"""
        conn = sqlite3.connect(self.grader.db_path)
        
        # Get training data counts from submissions table
        # Use ABS() to ensure scores are always positive
        stats = pd.read_sql_query("""
            SELECT 
                COUNT(CASE WHEN ai_score IS NOT NULL THEN 1 END) as total_samples,
                COUNT(CASE WHEN human_score IS NOT NULL THEN 1 END) as corrected_samples,
                COUNT(CASE WHEN human_feedback IS NOT NULL THEN 1 END) as feedback_samples,
                AVG(CASE WHEN human_score IS NOT NULL THEN ABS(human_score) END) as avg_human_score,
                AVG(CASE WHEN ai_score IS NOT NULL THEN ABS(ai_score) END) as avg_ai_score
            FROM submissions
        """, conn)
        
        conn.close()
        
        if not stats.empty:
            row = stats.iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Samples", 
                    int(row['total_samples']),
                    help="Total number of graded submissions"
                )
            
            with col2:
                st.metric(
                    "Corrected Samples", 
                    int(row['corrected_samples']),
                    help="Submissions with instructor corrections"
                )
            
            with col3:
                correction_rate = (row['corrected_samples'] / row['total_samples'] * 100) if row['total_samples'] > 0 else 0
                st.metric(
                    "Correction Rate", 
                    f"{correction_rate:.1f}%",
                    help="Percentage of samples with corrections"
                )
            
            with col4:
                if row['avg_human_score'] and row['avg_ai_score']:
                    score_diff = abs(row['avg_human_score'] - row['avg_ai_score'])
                    st.metric(
                        "Avg Score Difference", 
                        f"{score_diff:.1f}",
                        help="Average difference between AI and human scores"
                    )
    
    def show_correction_interface(self):
        """Interface for reviewing and correcting AI grades - SPLIT SCREEN VERSION"""
        st.subheader("Review AI Grades")
        
        # Add CSS for fixed height scrollable panels
        st.markdown("""
            <style>
            /* Make the main content area use full viewport height */
            .main .block-container {
                max-height: 100vh;
                padding-top: 2rem;
                padding-bottom: 1rem;
            }
            
            /* Fixed height scrollable columns */
            div[data-testid="column"] {
                height: calc(100vh - 250px);
                overflow-y: auto;
                overflow-x: hidden;
                padding-right: 10px;
            }
            
            /* Custom scrollbar */
            div[data-testid="column"]::-webkit-scrollbar {
                width: 8px;
            }
            
            div[data-testid="column"]::-webkit-scrollbar-track {
                background: #262730;
                border-radius: 4px;
            }
            
            div[data-testid="column"]::-webkit-scrollbar-thumb {
                background: #4a4a5e;
                border-radius: 4px;
            }
            
            div[data-testid="column"]::-webkit-scrollbar-thumb:hover {
                background: #5a5a6e;
            }
            
            /* Prevent horizontal scrolling on main container */
            .main {
                overflow-x: hidden;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Filter options and bulk actions at the top
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        
        with col1:
            # Assignment filter
            conn = sqlite3.connect(self.grader.db_path)
            assignments = pd.read_sql_query("SELECT id, name FROM assignments", conn)
            conn.close()
            
            assignment_options = ["All Assignments"] + assignments['name'].tolist()
            selected_assignment = st.selectbox("Filter by Assignment", assignment_options)
        
        with col2:
            # Status filter
            status_filter = st.selectbox("Filter by Status", [
                "Needs Review", "Already Corrected", "All"
            ])
        
        with col3:
            st.write("")  # Spacing
            if st.button("🗑️ Clear List", help="Clear training data to manage list size"):
                self._show_clear_options(selected_assignment)
        
        with col4:
            st.write("")  # Spacing
            # Bulk report generation will be added below after we get submissions
        
        # Get submissions to review
        submissions = self.get_submissions_for_review(selected_assignment, status_filter)
        
        if submissions.empty:
            st.info("No submissions found matching your criteria.")
            return
        
        # Bulk report generation buttons
        st.markdown("---")
        col_a, col_b, col_c = st.columns([1, 1, 2])
        
        with col_a:
            if st.button("📄 Generate All PDFs", use_container_width=True, help="Generate individual PDF reports for all submissions"):
                self._generate_bulk_pdf_reports(submissions)
        
        with col_b:
            if st.button("📊 Export to CSV", use_container_width=True, help="Export all grades and feedback to CSV"):
                self._export_to_csv(submissions)
        
        st.markdown("---")
        
        # SPLIT SCREEN LAYOUT with fixed heights
        left_panel, right_panel = st.columns([1, 2])
        
        # LEFT PANEL: Submission List (Scrollable)
        with left_panel:
            st.markdown("### 📋 Submissions")
            st.caption(f"Showing {len(submissions)} submissions")
            
            # Initialize selected submission in session state
            if 'selected_submission_idx' not in st.session_state:
                st.session_state.selected_submission_idx = 0
            
            # Create scrollable container for submission list
            with st.container():
                # Render submission list
                for idx, submission in submissions.iterrows():
                    self._render_submission_button(submission, idx)
        
        # RIGHT PANEL: Selected Submission Details (Scrollable)
        with right_panel:
            # Create scrollable container for details
            with st.container():
                if len(submissions) > 0:
                    selected_idx = st.session_state.selected_submission_idx
                    if selected_idx < len(submissions):
                        selected_submission = submissions.iloc[selected_idx]
                        self._render_submission_details(selected_submission)
                    else:
                        st.info("Select a submission from the list")
                else:
                    st.info("No submissions to display")
    
    def _render_submission_button(self, submission, idx):
        """Render a clickable submission button in the list"""
        # Get score in points (ensure positive)
        score_points = abs(submission.get('final_score') or submission.get('ai_score') or 0)
        
        # Get max score from assignment (default to 100 if not set)
        max_score = submission.get('max_score', 100)
        
        # Calculate percentage
        score_percentage = (score_points / max_score) * 100 if max_score > 0 else 0
        
        # Determine rating based on percentage
        if score_percentage >= 90:
            score_emoji = "🟢"
            score_label = "Excellent"
        elif score_percentage >= 80:
            score_emoji = "🟡"
            score_label = "Good"
        elif score_percentage >= 70:
            score_emoji = "🟠"
            score_label = "Fair"
        else:
            score_emoji = "🔴"
            score_label = "Poor"
        
        # Check if this is the selected submission
        is_selected = st.session_state.selected_submission_idx == idx
        button_type = "primary" if is_selected else "secondary"
        
        # Create button
        if st.button(
            f"{score_emoji} {submission.get('student_name', 'Unknown')}",
            key=f"sub_btn_{submission['id']}",
            use_container_width=True,
            type=button_type
        ):
            st.session_state.selected_submission_idx = idx
            st.rerun()
        
        # Show score and status below button
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"{score_points:.1f}/{max_score} ({score_percentage:.0f}%)")
        with col2:
            if submission.get('human_score') is not None:
                st.caption("✅ Reviewed")
            else:
                st.caption("🤖 AI only")
        
        st.divider()
    
    def _render_submission_details(self, submission):
        """Render detailed view of selected submission in right panel"""
        st.markdown(f"### 📝 {submission.get('student_name', 'Unknown')}")
        st.caption(f"Assignment: {submission['assignment_name']}")
        
        # Individual report button
        if st.button("📄 Generate PDF Report", key=f"pdf_{submission['id']}", use_container_width=True):
            self._generate_individual_pdf_report(submission)
        
        st.markdown("---")
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 AI Feedback", "📓 Notebook", "✍️ Your Review"])
        
        with tab1:
            self._render_ai_feedback_tab(submission)
        
        with tab2:
            self._render_notebook_tab(submission)
        
        with tab3:
            self._render_review_form_tab(submission)
    
    def _render_ai_feedback_tab(self, submission):
        """Render AI feedback in a tab"""
        st.markdown("**AI Assessment:**")
        st.metric("AI Score", f"{abs(submission['ai_score']):.1f}/37.5")
        
        if submission['ai_feedback']:
            try:
                feedback_data = json.loads(submission['ai_feedback'])
                
                if isinstance(feedback_data, dict) and 'comprehensive_feedback' in feedback_data:
                    comp_feedback = feedback_data['comprehensive_feedback']
                    
                    # Show instructor comments
                    if 'instructor_comments' in comp_feedback:
                        st.markdown("**Overall Assessment:**")
                        st.info(comp_feedback['instructor_comments'])
                    
                    # Show detailed feedback sections
                    if 'detailed_feedback' in comp_feedback:
                        detailed = comp_feedback['detailed_feedback']
                        
                        for section_name in ['reflection_assessment', 'analytical_strengths', 'areas_for_development']:
                            if section_name in detailed and detailed[section_name]:
                                section_title = section_name.replace('_', ' ').title()
                                with st.expander(f"**{section_title}**"):
                                    for item in detailed[section_name]:
                                        st.write(f"• {item}")
                
                elif isinstance(feedback_data, list):
                    for item in feedback_data:
                        st.write(f"• {item}")
                else:
                    st.write(str(feedback_data))
                    
            except:
                st.write(str(submission['ai_feedback']))
    
    def _render_notebook_tab(self, submission):
        """Render notebook content in a tab"""
        if submission['cell_content'] and os.path.exists(submission['cell_content']):
            if st.button("📖 Load Notebook Content", key=f"load_nb_{submission['id']}"):
                self.show_notebook_content(submission['cell_content'])
        else:
            st.warning("Notebook file not found")
    
    def _render_review_form_tab(self, submission):
        """Render the review form in a tab"""
        st.markdown("**Your Assessment:**")
        
        # Show smart suggestions
        if submission['cell_content'] and os.path.exists(submission['cell_content']):
            try:
                with open(submission['cell_content'], 'r') as f:
                    content = f.read()
                suggestions = CorrectionHelpers.suggest_score_adjustment(
                    submission['ai_score'], content, {}
                )
                if suggestions:
                    st.markdown("**💡 Suggestions:**")
                    for suggestion in suggestions:
                        st.info(suggestion)
            except:
                pass
        
        # Correction form
        with st.form(f"correction_{submission['id']}"):
            corrected_score = st.number_input(
                "Corrected Score (out of 37.5)",
                min_value=0.0,
                max_value=37.5,
                value=float(abs(submission['human_score'])) if submission['human_score'] else float(abs(submission['ai_score'])),
                step=0.5,
                key=f"score_{submission['id']}"
            )
            
            # Show feedback template suggestion
            if not submission['human_feedback']:
                template = CorrectionHelpers.generate_feedback_template(corrected_score)
                st.markdown("**💬 Suggested feedback:**")
                st.caption(template)
            
            corrected_feedback = st.text_area(
                "Corrected Feedback",
                value=submission['human_feedback'] if submission['human_feedback'] else "",
                height=150,
                key=f"feedback_{submission['id']}"
            )
            
            # Show feedback improvement suggestions
            if corrected_score != submission['ai_score']:
                adjustment = corrected_score - submission['ai_score']
                feedback_suggestions = CorrectionHelpers.smart_feedback_suggestions(
                    "", submission['ai_feedback'], adjustment
                )
                if feedback_suggestions:
                    st.markdown("**📝 Feedback tips:**")
                    for tip in feedback_suggestions:
                        st.caption(tip)
            
            col_a, col_b = st.columns(2)
            with col_a:
                save_correction = st.form_submit_button("💾 Save Correction", use_container_width=True)
            with col_b:
                approve_ai = st.form_submit_button("✅ Approve AI Grade", use_container_width=True)
            
            if save_correction:
                self.save_correction(submission['id'], corrected_score, corrected_feedback)
                st.success("Correction saved!")
                st.rerun()
            
            if approve_ai:
                self.save_correction(submission['id'], submission['ai_score'], submission['ai_feedback'])
                st.success("AI grade approved!")
                st.rerun()
    
    def get_submissions_for_review(self, assignment_filter, status_filter):
        """Get submissions that need review based on filters"""
        conn = sqlite3.connect(self.grader.db_path)
        conn.row_factory = sqlite3.Row
        
        # Updated query to use submissions table (where Business Analytics Grader stores data)
        # Use ABS() to ensure scores are always positive
        query = """
            SELECT 
                s.id,
                s.assignment_id,
                s.notebook_path as cell_content,
                ABS(s.ai_score) as ai_score,
                s.ai_feedback,
                ABS(s.human_score) as human_score,
                s.human_feedback,
                ABS(COALESCE(s.final_score, s.ai_score)) as final_score,
                s.submission_date as created_date,
                a.name as assignment_name,
                a.total_points as max_score,
                COALESCE(st.name, 'Unknown') as student_name,
                COALESCE(st.student_id, 'Unknown') as student_id
            FROM submissions s
            JOIN assignments a ON s.assignment_id = a.id
            LEFT JOIN students st ON s.student_id = st.id
            WHERE s.ai_score IS NOT NULL
        """
        
        params = []
        
        if assignment_filter != "All Assignments":
            query += " AND a.name = ?"
            params.append(assignment_filter)
        
        if status_filter == "Needs Review":
            query += " AND s.human_score IS NULL"
        elif status_filter == "Already Corrected":
            query += " AND s.human_score IS NOT NULL"
        
        query += " ORDER BY s.submission_date DESC"
        
        submissions = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return submissions
    
    def show_submission_review(self, submission):
        """Show individual submission for review"""
        with st.expander(f"📋 {submission['assignment_name']} - {submission.get('student_name', 'Unknown')}"):
            
            # Show AI assessment
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**AI Assessment:**")
                st.write(f"Score: {abs(submission['ai_score'])}/37.5")
                if submission['ai_feedback']:
                    st.write("Feedback:")
                    try:
                        # Try to parse comprehensive feedback
                        feedback_data = json.loads(submission['ai_feedback'])
                        
                        if isinstance(feedback_data, dict) and 'comprehensive_feedback' in feedback_data:
                            comp_feedback = feedback_data['comprehensive_feedback']
                            
                            # Show instructor comments
                            if 'instructor_comments' in comp_feedback:
                                st.write("**Overall Assessment:**")
                                st.write(comp_feedback['instructor_comments'][:200] + "..." if len(comp_feedback['instructor_comments']) > 200 else comp_feedback['instructor_comments'])
                            
                            # Show key sections (condensed)
                            if 'detailed_feedback' in comp_feedback:
                                detailed = comp_feedback['detailed_feedback']
                                
                                # Show first few items from key sections
                                for section_name in ['reflection_assessment', 'analytical_strengths', 'areas_for_development']:
                                    if section_name in detailed and detailed[section_name]:
                                        section_title = section_name.replace('_', ' ').title()
                                        st.write(f"**{section_title}:**")
                                        for item in detailed[section_name][:2]:  # Show first 2 items
                                            st.write(f"• {item}")
                                        if len(detailed[section_name]) > 2:
                                            st.write(f"... and {len(detailed[section_name]) - 2} more")
                                        st.write("")
                        
                        elif isinstance(feedback_data, list):
                            # Legacy format
                            for item in feedback_data[:3]:  # Show first 3 items
                                st.write(f"• {item}")
                            if len(feedback_data) > 3:
                                st.write(f"... and {len(feedback_data) - 3} more items")
                        
                        else:
                            st.write(str(feedback_data)[:300] + "..." if len(str(feedback_data)) > 300 else str(feedback_data))
                            
                    except:
                        # Fallback for non-JSON feedback
                        feedback_text = str(submission['ai_feedback'])
                        st.write(feedback_text[:300] + "..." if len(feedback_text) > 300 else feedback_text)
                
                # Show smart suggestions
                if submission['cell_content'] and os.path.exists(submission['cell_content']):
                    try:
                        with open(submission['cell_content'], 'r') as f:
                            content = f.read()
                        suggestions = CorrectionHelpers.suggest_score_adjustment(
                            submission['ai_score'], content, {}
                        )
                        if suggestions:
                            st.markdown("**💡 Suggestions:**")
                            for suggestion in suggestions:
                                st.info(suggestion)
                    except:
                        pass
            
            with col2:
                st.markdown("**Your Assessment:**")
                
                # Correction form
                with st.form(f"correction_{submission['id']}"):
                    corrected_score = st.number_input(
                        "Corrected Score (out of 37.5)",
                        min_value=0.0,
                        max_value=37.5,
                        value=float(submission['human_score']) if submission['human_score'] else float(submission['ai_score']),
                        step=0.5,
                        key=f"score_{submission['id']}"
                    )
                    
                    # Show feedback template suggestion
                    if not submission['human_feedback']:
                        template = CorrectionHelpers.generate_feedback_template(corrected_score)
                        st.markdown("**💬 Suggested feedback:**")
                        st.write(template)
                    
                    corrected_feedback = st.text_area(
                        "Corrected Feedback",
                        value=submission['human_feedback'] if submission['human_feedback'] else "",
                        height=100,
                        key=f"feedback_{submission['id']}"
                    )
                    
                    # Show feedback improvement suggestions
                    if corrected_score != submission['ai_score']:
                        adjustment = corrected_score - submission['ai_score']
                        feedback_suggestions = CorrectionHelpers.smart_feedback_suggestions(
                            "", submission['ai_feedback'], adjustment
                        )
                        if feedback_suggestions:
                            st.markdown("**📝 Feedback tips:**")
                            for tip in feedback_suggestions:
                                st.caption(tip)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        save_correction = st.form_submit_button("💾 Save Correction")
                    with col_b:
                        approve_ai = st.form_submit_button("✅ Approve AI Grade")
                    
                    if save_correction:
                        self.save_correction(submission['id'], corrected_score, corrected_feedback)
                        st.success("Correction saved!")
                        st.rerun()
                    
                    if approve_ai:
                        self.save_correction(submission['id'], submission['ai_score'], submission['ai_feedback'])
                        st.success("AI grade approved!")
                        st.rerun()
            
            # Show notebook content (if available)
            if st.button(f"📖 View Notebook", key=f"view_{submission['id']}"):
                self.show_notebook_content(submission['cell_content'])
    
    def save_correction(self, submission_id, score, feedback):
        """Save instructor correction to submissions table"""
        conn = sqlite3.connect(self.grader.db_path)
        cursor = conn.cursor()
        
        # Update submissions table (where Business Analytics Grader data is stored)
        cursor.execute("""
            UPDATE submissions
            SET human_score = ?, human_feedback = ?, final_score = ?
            WHERE id = ?
        """, (score, feedback, score, submission_id))
        
        conn.commit()
        
        # Also add to ai_training_data for historical tracking (optional)
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO ai_training_data 
                (assignment_id, cell_content, ai_score, ai_feedback, human_score, human_feedback, corrected_at)
                SELECT assignment_id, notebook_path, ai_score, ai_feedback, ?, ?, ?
                FROM submissions WHERE id = ?
            """, (score, feedback, datetime.now().isoformat(), submission_id))
            conn.commit()
        except:
            pass  # Don't fail if ai_training_data insert fails
        
        conn.close()
        conn.close()
    
    def show_notebook_content(self, notebook_path):
        """Display notebook content for review"""
        try:
            import nbformat
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
            
            st.markdown("**Notebook Content:**")
            for i, cell in enumerate(nb.cells):
                if cell.cell_type == 'code':
                    st.code(cell.source, language='r')
                elif cell.cell_type == 'markdown':
                    st.markdown(cell.source)
                    
        except Exception as e:
            st.error(f"Could not load notebook: {e}")
    
    def show_training_progress(self):
        """Show training progress over time"""
        st.subheader("Training Progress")
        
        conn = sqlite3.connect(self.grader.db_path)
        
        # Progress over time
        progress_data = pd.read_sql_query("""
            SELECT 
                DATE(created_date) as date,
                COUNT(*) as total_samples,
                COUNT(CASE WHEN human_score IS NOT NULL THEN 1 END) as corrected_samples
            FROM ai_training_data
            GROUP BY DATE(created_date)
            ORDER BY date
        """, conn)
        
        if not progress_data.empty:
            progress_data['correction_rate'] = progress_data['corrected_samples'] / progress_data['total_samples'] * 100
            
            fig = px.line(progress_data, x='date', y='correction_rate', 
                         title='Correction Rate Over Time',
                         labels={'correction_rate': 'Correction Rate (%)', 'date': 'Date'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Score accuracy analysis
        accuracy_data = pd.read_sql_query("""
            SELECT 
                ai_score,
                human_score,
                ABS(ai_score - human_score) as score_difference
            FROM ai_training_data
            WHERE human_score IS NOT NULL AND ai_score IS NOT NULL
        """, conn)
        
        conn.close()
        
        if not accuracy_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.scatter(accuracy_data, x='ai_score', y='human_score',
                               title='AI vs Human Scores',
                               labels={'ai_score': 'AI Score', 'human_score': 'Human Score'})
                fig.add_shape(type="line", x0=0, y0=0, x1=100, y1=100, 
                             line=dict(dash="dash", color="red"))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.histogram(accuracy_data, x='score_difference',
                                 title='Score Difference Distribution',
                                 labels={'score_difference': 'Score Difference'})
                st.plotly_chart(fig, use_container_width=True)
    
    def show_retraining_interface(self):
        """Interface for retraining the AI model"""
        st.subheader("Retrain AI Model")
        
        conn = sqlite3.connect(self.grader.db_path)
        training_count = pd.read_sql_query("""
            SELECT COUNT(*) as count FROM ai_training_data
            WHERE human_score IS NOT NULL
        """, conn).iloc[0]['count']
        conn.close()
        
        st.write(f"**Available training samples:** {training_count}")
        
        if training_count < 10:
            st.warning("Need at least 10 corrected samples to retrain the model.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            training_scope = st.selectbox("Training Scope", [
                "Global Model (All Assignments)",
                "Language-Specific Model", 
                "Individual Assignment Model"
            ])
            
            assignment_id = None
            language_filter = None
            
            if training_scope == "Language-Specific Model":
                language_type = st.selectbox("Select Language", ["R", "SQL", "Python", "Other"])
                language_filter = language_type
                
            elif training_scope == "Individual Assignment Model":
                conn = sqlite3.connect(self.grader.db_path)
                assignments = pd.read_sql_query("SELECT id, name FROM assignments", conn)
                conn.close()
                
                if not assignments.empty:
                    selected_assignment = st.selectbox("Select Assignment", assignments['name'].tolist())
                    assignment_id = assignments[assignments['name'] == selected_assignment]['id'].iloc[0]
        
        with col2:
            st.write("**Training Options:**")
            include_feedback = st.checkbox("Include feedback text in training", value=True)
            cross_validate = st.checkbox("Perform cross-validation", value=True)
        
        if st.button("🚀 Start Retraining"):
            with st.spinner("Retraining model..."):
                success, message = self.ai_grader.train_model(
                    assignment_id=assignment_id, 
                    language_filter=language_filter
                )
                
                if success:
                    st.success(f"✅ {message}")
                    
                    # Show training results
                    if cross_validate:
                        self.show_cross_validation_results(assignment_id)
                else:
                    st.error(f"❌ Training failed: {message}")
    
    def show_cross_validation_results(self, assignment_id=None):
        """Show cross-validation results after training"""
        # This would implement k-fold cross-validation
        # For now, show a placeholder
        st.info("Cross-validation results would be displayed here")
    
    def show_performance_analytics(self):
        """Show detailed performance analytics"""
        st.subheader("Performance Analytics")
        
        conn = sqlite3.connect(self.grader.db_path)
        
        # Performance by assignment
        perf_by_assignment = pd.read_sql_query("""
            SELECT 
                a.name as assignment_name,
                COUNT(*) as total_samples,
                COUNT(CASE WHEN td.human_score IS NOT NULL THEN 1 END) as corrected_samples,
                AVG(CASE WHEN td.human_score IS NOT NULL THEN ABS(td.ai_score - td.human_score) END) as avg_error
            FROM ai_training_data td
            JOIN assignments a ON td.assignment_id = a.id
            WHERE td.ai_score IS NOT NULL
            GROUP BY a.id, a.name
        """, conn)
        
        if not perf_by_assignment.empty:
            fig = px.bar(perf_by_assignment, x='assignment_name', y='avg_error',
                        title='Average Grading Error by Assignment',
                        labels={'avg_error': 'Average Error', 'assignment_name': 'Assignment'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Common correction patterns
        st.subheader("Common Correction Patterns")
        
        corrections = pd.read_sql_query("""
            SELECT 
                ai_score,
                human_score,
                (human_score - ai_score) as correction_amount,
                human_feedback
            FROM ai_training_data
            WHERE human_score IS NOT NULL AND ai_score IS NOT NULL
        """, conn)
        
        conn.close()
        
        if not corrections.empty:
            # Show most common correction types
            corrections['correction_type'] = corrections['correction_amount'].apply(
                lambda x: 'Increased Score' if x > 2 else ('Decreased Score' if x < -2 else 'Minor Adjustment')
            )
            
            correction_counts = corrections['correction_type'].value_counts()
            
            fig = px.pie(values=correction_counts.values, names=correction_counts.index,
                        title='Types of Corrections Made')
            st.plotly_chart(fig, use_container_width=True)
            
            # Show feedback patterns
            if corrections['human_feedback'].notna().any():
                st.subheader("Common Feedback Themes")
                feedback_text = ' '.join(corrections['human_feedback'].dropna().tolist())
                
                # Simple word frequency (you could enhance this with NLP)
                words = feedback_text.lower().split()
                word_freq = pd.Series(words).value_counts().head(20)
                
                fig = px.bar(x=word_freq.index, y=word_freq.values,
                           title='Most Common Words in Feedback')
                st.plotly_chart(fig, use_container_width=True)
    
    def show_setup_helper(self):
        """Show assignment setup and course planning helpers"""
        st.subheader("Assignment & Course Setup")
        
        helper_type = st.selectbox("Choose Helper", [
            "Assignment Setup Wizard",
            "Course Training Planner"
        ])
        
        if helper_type == "Assignment Setup Wizard":
            AssignmentSetupHelper.show_assignment_setup_wizard()
        else:
            AssignmentSetupHelper.show_course_planning_helper()
    
    def show_alternative_approaches(self):
        """Show alternative approach configuration and examples"""
        st.subheader("Alternative Approach Handling")
        
        approach_tab1, approach_tab2, approach_tab3 = st.tabs([
            "⚙️ Flexibility Settings",
            "📚 Valid Examples", 
            "🔍 Approach Analysis"
        ])
        
        with approach_tab1:
            AlternativeApproachHandler.show_approach_flexibility_settings()
        
        with approach_tab2:
            AlternativeApproachHandler.create_approach_examples()
        
        with approach_tab3:
            st.markdown("### Analyze Student vs Solution Approaches")
            
            col1, col2 = st.columns(2)
            
            with col1:
                student_code = st.text_area("Student Code Sample", height=200)
                
            with col2:
                solution_code = st.text_area("Solution Code Sample", height=200)
            
            language = st.selectbox("Language", ["R", "SQL"])
            
            if st.button("🔍 Analyze Approaches") and student_code and solution_code:
                differences = AlternativeApproachHandler.analyze_approach_differences(
                    student_code, solution_code, language
                )
                
                if differences:
                    st.subheader("Approach Differences Found:")
                    for diff in differences:
                        if diff["is_valid"]:
                            st.success(f"✅ **{diff['type']}**: {diff['note']}")
                        else:
                            st.warning(f"⚠️ **{diff['type']}**: {diff['note']}")
                    
                    feedback = AlternativeApproachHandler.generate_alternative_approach_feedback(differences)
                    st.subheader("Generated Feedback:")
                    st.markdown(feedback)
                else:
                    st.info("No significant approach differences detected.")    

    def _show_clear_options(self, selected_assignment):
        """Show options for clearing training data"""
        st.subheader("🗑️ Clear Training Data")
        
        conn = sqlite3.connect(self.grader.db_path)
        cursor = conn.cursor()
        
        # Get counts for different clear options
        cursor.execute("SELECT COUNT(*) FROM ai_training_data")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ai_training_data WHERE human_score IS NOT NULL")
        corrected_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ai_training_data WHERE human_score IS NULL")
        uncorrected_count = cursor.fetchone()[0]
        
        if selected_assignment != "All Assignments":
            cursor.execute("SELECT id FROM assignments WHERE name = ?", (selected_assignment,))
            assignment_id = cursor.fetchone()
            if assignment_id:
                cursor.execute("SELECT COUNT(*) FROM ai_training_data WHERE assignment_id = ?", (assignment_id[0],))
                assignment_count = cursor.fetchone()[0]
        
        conn.close()
        
        st.write(f"**Current training data:** {total_count} total entries")
        st.write(f"- {corrected_count} corrected entries")
        st.write(f"- {uncorrected_count} uncorrected entries")
        
        if selected_assignment != "All Assignments" and 'assignment_count' in locals():
            st.write(f"- {assignment_count} entries for {selected_assignment}")
        
        st.warning("⚠️ **Warning:** Clearing training data will permanently delete the selected entries. This cannot be undone!")
        
        # Clear options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"Clear Uncorrected Only ({uncorrected_count} entries)", 
                        type="secondary",
                        help="Remove only entries that haven't been manually corrected"):
                if self._confirm_clear("uncorrected"):
                    self._clear_training_data("uncorrected")
                    st.success("✅ Cleared uncorrected entries")
                    st.rerun()
        
        with col2:
            if selected_assignment != "All Assignments" and 'assignment_count' in locals():
                if st.button(f"Clear {selected_assignment} ({assignment_count} entries)",
                            type="secondary", 
                            help=f"Remove all entries for {selected_assignment}"):
                    if self._confirm_clear("assignment", selected_assignment):
                        self._clear_training_data("assignment", selected_assignment)
                        st.success(f"✅ Cleared entries for {selected_assignment}")
                        st.rerun()
        
        # Dangerous options
        st.write("---")
        st.write("**⚠️ Dangerous Operations:**")
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button(f"Clear All Corrected ({corrected_count} entries)",
                        type="secondary",
                        help="Remove entries that have been manually corrected"):
                if self._confirm_clear("corrected"):
                    self._clear_training_data("corrected")
                    st.success("✅ Cleared corrected entries")
                    st.rerun()
        
        with col4:
            if st.button(f"Clear Everything ({total_count} entries)",
                        type="primary",
                        help="Remove ALL training data"):
                if self._confirm_clear("all"):
                    self._clear_training_data("all")
                    st.success("✅ Cleared all training data")
                    st.rerun()
    
    def _confirm_clear(self, clear_type, assignment_name=None):
        """Confirm clear operation"""
        if clear_type == "uncorrected":
            return st.checkbox("✅ I understand this will delete all uncorrected training data")
        elif clear_type == "corrected":
            return st.checkbox("✅ I understand this will delete all manually corrected training data")
        elif clear_type == "assignment":
            return st.checkbox(f"✅ I understand this will delete all training data for {assignment_name}")
        elif clear_type == "all":
            return st.checkbox("✅ I understand this will delete ALL training data permanently")
        return False
    
    def _clear_training_data(self, clear_type, assignment_name=None):
        """Clear training data based on type"""
        conn = sqlite3.connect(self.grader.db_path)
        cursor = conn.cursor()
        
        try:
            if clear_type == "uncorrected":
                cursor.execute("DELETE FROM ai_training_data WHERE human_score IS NULL")
            elif clear_type == "corrected":
                cursor.execute("DELETE FROM ai_training_data WHERE human_score IS NOT NULL")
            elif clear_type == "assignment":
                cursor.execute("""
                    DELETE FROM ai_training_data 
                    WHERE assignment_id = (SELECT id FROM assignments WHERE name = ?)
                """, (assignment_name,))
            elif clear_type == "all":
                cursor.execute("DELETE FROM ai_training_data")
            
            conn.commit()
            
        except Exception as e:
            st.error(f"Error clearing data: {e}")
        finally:
            conn.close()
    

    def _generate_individual_pdf_report(self, submission):
        """Generate PDF report for individual submission"""
        try:
            from report_generator import PDFReportGenerator
            
            # Prepare analysis result
            analysis_result = {
                'student_name': submission.get('student_name', 'Unknown'),
                'assignment_name': submission['assignment_name'],
                'final_score': abs(submission.get('final_score', submission.get('ai_score', 0))),
                'max_score': submission.get('max_score', 37.5),
                'submission_date': submission.get('created_date', ''),
                'comprehensive_feedback': json.loads(submission['ai_feedback']) if submission.get('ai_feedback') else {}
            }
            
            # Generate report
            generator = PDFReportGenerator()
            report_path = generator.generate_report(
                student_name=analysis_result['student_name'],
                assignment_id=analysis_result['assignment_name'],
                analysis_result=analysis_result
            )
            
            st.success(f"✅ Report generated: {report_path}")
            
            # Offer download
            with open(report_path, 'rb') as f:
                st.download_button(
                    label="⬇️ Download PDF",
                    data=f,
                    file_name=os.path.basename(report_path),
                    mime="application/pdf",
                    key=f"download_{submission['id']}"
                )
                
        except Exception as e:
            st.error(f"Error generating report: {e}")
    
    def _generate_bulk_pdf_reports(self, submissions):
        """Generate PDF reports for all submissions"""
        try:
            from report_generator import PDFReportGenerator
            
            generator = PDFReportGenerator()
            success_count = 0
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, submission in submissions.iterrows():
                status_text.text(f"Generating report {idx+1}/{len(submissions)}: {submission.get('student_name', 'Unknown')}")
                
                try:
                    # Prepare analysis result
                    analysis_result = {
                        'student_name': submission.get('student_name', 'Unknown'),
                        'assignment_name': submission['assignment_name'],
                        'final_score': abs(submission.get('final_score', submission.get('ai_score', 0))),
                        'max_score': submission.get('max_score', 37.5),
                        'submission_date': submission.get('created_date', ''),
                        'comprehensive_feedback': json.loads(submission['ai_feedback']) if submission.get('ai_feedback') else {}
                    }
                    
                    # Generate report
                    generator.generate_report(
                        student_name=analysis_result['student_name'],
                        assignment_id=analysis_result['assignment_name'],
                        analysis_result=analysis_result
                    )
                    
                    success_count += 1
                    
                except Exception as e:
                    st.warning(f"Failed to generate report for {submission.get('student_name', 'Unknown')}: {e}")
                
                progress_bar.progress((idx + 1) / len(submissions))
            
            status_text.empty()
            progress_bar.empty()
            
            st.success(f"✅ Generated {success_count}/{len(submissions)} PDF reports")
            
        except Exception as e:
            st.error(f"Error in bulk report generation: {e}")
    
    def _export_to_csv(self, submissions):
        """Export submissions to CSV"""
        try:
            import csv
            from io import StringIO
            
            # Prepare data for CSV
            csv_data = []
            
            for idx, submission in submissions.iterrows():
                score = abs(submission.get('final_score', submission.get('ai_score', 0)))
                max_score = submission.get('max_score', 37.5)
                percentage = (score / max_score * 100) if max_score > 0 else 0
                
                csv_data.append({
                    'Student Name': submission.get('student_name', 'Unknown'),
                    'Student ID': submission.get('student_id', 'Unknown'),
                    'Assignment': submission['assignment_name'],
                    'AI Score': abs(submission.get('ai_score', 0)),
                    'Human Score': abs(submission.get('human_score', 0)) if submission.get('human_score') else '',
                    'Final Score': score,
                    'Max Score': max_score,
                    'Percentage': f"{percentage:.1f}%",
                    'Status': 'Human Reviewed' if submission.get('human_score') else 'AI Only',
                    'Submission Date': submission.get('created_date', '')
                })
            
            # Convert to DataFrame
            df = pd.DataFrame(csv_data)
            
            # Convert to CSV
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_string = csv_buffer.getvalue()
            
            # Offer download
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_string,
                file_name=f"grades_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="csv_download"
            )
            
            st.success(f"✅ Exported {len(csv_data)} submissions to CSV")
            
        except Exception as e:
            st.error(f"Error exporting to CSV: {e}")
