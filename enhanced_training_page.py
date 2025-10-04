#!/usr/bin/env python3
"""
Enhanced AI Training Page
Main Streamlit page for the enhanced training interface
"""

import streamlit as st
import pandas as pd
import json
import os
import tempfile
import zipfile
from datetime import datetime
from enhanced_training_interface import EnhancedTrainingInterface, display_interactive_notebook
from enhanced_training_database import setup_enhanced_training_database
import nbformat
from nbformat import NotebookNode
from nbconvert import HTMLExporter
from anonymization_utils import anonymize_name, anonymize_student_id

def display_notebook_with_outputs(notebook_path):
    """Display notebook with HTML rendering - same as review page"""
    if not notebook_path or not os.path.exists(notebook_path):
        st.warning("Notebook file not found")
        return
    
    try:
        # Convert notebook to HTML for display (same as review page)
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        html_exporter = HTMLExporter()
        html_exporter.template_name = 'classic'
        (body, resources) = html_exporter.from_notebook_node(nb)
        
        # Display HTML in MUCH LONGER scrollable container
        st.components.v1.html(body, height=2000, scrolling=True)
        
    except Exception as e:
        st.error(f"Error displaying notebook: {str(e)}")
        # Fallback: show raw content
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                content = f.read()
            st.code(content[:5000], language='json')  # Show first 5000 chars
        except:
            st.error("Could not load notebook content")

def enhanced_training_page():
    """Main review and grading page"""
    
    st.title("📝 Review & Grade")
    st.caption("Review and correct AI-generated scores")
    
    # Initialize enhanced training interface
    try:
        # Set up database if needed
        setup_enhanced_training_database()
        training = EnhancedTrainingInterface()
    except Exception as e:
        st.error(f"Failed to initialize training interface: {e}")
        return
    
    # Assignment selection
    assignments = training.get_assignments()
    if not assignments:
        st.warning("No assignments found in the database.")
        return
    
    # Assignment selector
    assignment_options = {
        f"{a['title']} ({a['submission_count']} submissions, {a['human_reviewed_count']} reviewed)": a['id'] 
        for a in assignments
    }
    selected_assignment_key = st.selectbox("Select Assignment", list(assignment_options.keys()))
    selected_assignment_id = assignment_options[selected_assignment_key]
    
    # Get assignment details
    selected_assignment = next(a for a in assignments if a['id'] == selected_assignment_id)
    
    # Display assignment statistics
    stats = training.get_training_stats(selected_assignment_id)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Submissions", stats['total_submissions'])
    with col2:
        st.metric("Human Reviewed", f"{stats['human_reviewed']} ({stats['review_percentage']}%)")
    with col3:
        st.metric("Avg AI Score", f"{stats['avg_ai_score']}/37.5")
    with col4:
        st.metric("AI Accuracy", f"{stats['ai_accuracy_percentage']}%")
    
    # Initialize demo mode in session state
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = False
    
    # Filtering section and Clear button
    col_filter, col_clear = st.columns([4, 1])
    
    with col_filter:
        with st.expander("🔍 Filters & Settings"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                score_range = st.slider("Score Range", 0.0, 37.5, (0.0, 37.5), step=0.5)
            
            with col2:
                review_status = st.selectbox("Review Status", [
                    "All", "AI Only", "Human Reviewed", "Needs Review"
                ])
            
            with col3:
                student_search = st.text_input("Search Student Name")
    
    with col_clear:
        st.write("")  # Spacing
        if st.button("🗑️ Clear Results", help="Clear submissions for this assignment", use_container_width=True):
            st.session_state.show_clear_confirm_training = True
    
    # Show confirmation dialog if requested
    if st.session_state.get('show_clear_confirm_training', False):
        st.warning("⚠️ This will permanently delete all submissions for this assignment!")
        col_confirm1, col_confirm2 = st.columns(2)
        
        with col_confirm1:
            if st.button("✅ Confirm Delete", type="primary"):
                import sqlite3
                conn = sqlite3.connect(training.db_path)
                cursor = conn.cursor()
                
                # Count before delete
                cursor.execute("SELECT COUNT(*) FROM submissions WHERE assignment_id = ?", (selected_assignment_id,))
                count_before = cursor.fetchone()[0]
                
                # Delete
                cursor.execute("DELETE FROM submissions WHERE assignment_id = ?", (selected_assignment_id,))
                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()
                
                st.success(f"✅ Deleted {deleted_count} submissions for this assignment (was {count_before})")
                st.session_state.show_clear_confirm_training = False
                st.rerun()
        
        with col_confirm2:
            if st.button("❌ Cancel"):
                st.session_state.show_clear_confirm_training = False
                st.rerun()
    
    # Apply filters
    filters = {
        'score_range': score_range,
        'review_status': review_status,
        'student_search': student_search
    }
    
    # Get filtered submissions
    submissions = training.get_submissions(selected_assignment_id, filters)
    
    if not submissions:
        st.warning("No submissions found matching your criteria.")
        return
    
    # Initialize session state for selected submission
    if 'selected_submission_id' not in st.session_state:
        st.session_state.selected_submission_id = submissions[0]['id']
    
    # Compact CSS for better space utilization
    st.markdown("""
    <style>
    .main .block-container { padding: 0.5rem 1rem !important; max-width: 100% !important; }
    .element-container { margin: 0 !important; padding: 0 !important; }
    .stVerticalBlock, .stVerticalBlock > div { gap: 0 !important; margin: 0 !important; padding: 0 !important; }
    .stButton { margin: 0 !important; padding: 0 !important; }
    .stButton button { height: 2rem !important; padding: 0.25rem 0.5rem !important; }
    h1 { font-size: 1.6rem !important; margin: 0.2rem 0 !important; line-height: 1.1 !important; }
    h2, h3 { font-size: 1rem !important; margin: 0.1rem 0 !important; line-height: 1.1 !important; }
    [data-testid="stMetric"] { padding: 0.1rem !important; }
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-thumb { background: #4a4a5e; border-radius: 4px; }
    ::-webkit-scrollbar-track { background: #1e1e1e; }
    </style>
    """, unsafe_allow_html=True)
    
    # Main dual-panel layout: Left 1/3, Right 2/3
    left_col, right_col = st.columns([1, 2])
    
    with left_col:
        st.subheader("📋 Submissions")
        
        # Create a scrollable container with fixed height for all content
        with st.container(height=800):
            # Bulk operations
            with st.expander("⚡ Bulk Operations"):
                col1, col2 = st.columns(2)
                
                with col1:
                    boost_percent = st.number_input("Boost %", min_value=1, max_value=20, value=5)
                    if st.button("📈 Boost All"):
                        filtered_ids = [s['id'] for s in submissions if s['human_score'] is None]
                        if filtered_ids:
                            success, message = training.apply_bulk_operation(
                                filtered_ids, "boost_percentage", boost_percent=boost_percent
                            )
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                
                with col2:
                    curve_points = st.number_input("Curve Points", min_value=0.5, max_value=5.0, value=2.0, step=0.5)
                    if st.button("📊 Apply Curve"):
                        filtered_ids = [s['id'] for s in submissions]
                        success, message = training.apply_bulk_operation(
                            filtered_ids, "apply_curve", curve_points=curve_points
                        )
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
            
            # Display submissions list with inline editing - COMPACT VERSION
            for idx, submission in enumerate(submissions):
                # Compact container for each student
                with st.container():
                    # Selection button
                    is_selected = submission['id'] == st.session_state.selected_submission_id
                    button_type = "primary" if is_selected else "secondary"
                    
                    display_name = anonymize_name(submission['student_name'], submission['student_id'])
                    if st.button(
                        f"{submission['grade_indicator']} {display_name}", 
                        key=f"select_{submission['id']}",
                        type=button_type,
                        use_container_width=True
                    ):
                        st.session_state.selected_submission_id = submission['id']
                        st.rerun()
                    
                    # Compact row with all controls
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    with col1:
                        st.markdown(f"<small style='color: #888; line-height: 1;'>{submission['score_status']}</small>", unsafe_allow_html=True)
                    with col2:
                        current_score = submission['human_score'] or submission['ai_score']
                        new_score = st.number_input(
                            "Score", 
                            min_value=0.0, 
                            max_value=37.5, 
                            value=float(current_score),
                            step=0.5,
                            key=f"score_{submission['id']}",
                            label_visibility="collapsed"
                        )
                    with col3:
                        if st.button("💾", key=f"save_{submission['id']}", help="Save score"):
                            if training.save_human_feedback(submission['id'], new_score, "Quick save from list"):
                                st.success("✓")
                                st.rerun()
                            else:
                                st.error("✗")
                    with col4:
                        if st.button("📄", key=f"pdf_{submission['id']}", help="Generate PDF"):
                            with st.spinner("Generating..."):
                                # Use SAME logic as review page - get full feedback, remove verbose arrays
                                from report_generator import PDFReportGenerator
                                report_gen = PDFReportGenerator()
                                
                                # Get submission data
                                conn = training.get_database_connection()
                                cursor = conn.cursor()
                                cursor.execute("SELECT * FROM submissions WHERE id = ?", (submission['id'],))
                                sub_data = cursor.fetchone()
                                conn.close()
                                
                                if sub_data and sub_data['ai_feedback']:
                                    try:
                                        analysis_result = json.loads(sub_data['ai_feedback'])
                                        # ai_feedback now contains updated instructor_comments if human reviewed
                                    except:
                                        analysis_result = {}
                                else:
                                    analysis_result = {}
                                
                                # Use final_score (which is human_score if reviewed, otherwise ai_score)
                                analysis_result['total_score'] = submission.get('final_score', submission['ai_score'])
                                
                                # Check if human reviewed
                                if sub_data and sub_data['human_score'] is not None:
                                    analysis_result['human_reviewed'] = True
                                    analysis_result['ai_score'] = submission['ai_score']  # Show original AI score for reference
                                else:
                                    analysis_result['human_reviewed'] = False
                                
                                analysis_result['max_score'] = 37.5
                                
                                display_name = anonymize_name(submission['student_name'], submission['student_id'])
                                pdf_path = report_gen.generate_report(
                                    student_name=display_name,
                                    assignment_id=selected_assignment['title'],
                                    analysis_result=analysis_result
                                )
                                if pdf_path and os.path.exists(pdf_path):
                                    with open(pdf_path, 'rb') as f:
                                        safe_name = "".join(c for c in display_name if c.isalnum() or c in (' ', '-', '_'))
                                        st.download_button(
                                            "⬇️",
                                            f.read(),
                                            file_name=f"{safe_name}_report.pdf",
                                            mime="application/pdf",
                                            key=f"dl_{submission['id']}"
                                        )
                                    try:
                                        os.unlink(pdf_path)
                                    except:
                                        pass
                                else:
                                    st.error("Failed")
                
                # Add spacing between student entries
                st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)
    
    with right_col:
        # Get selected submission details
        selected_submission = next(
            (s for s in submissions if s['id'] == st.session_state.selected_submission_id), 
            submissions[0]
        )
        
        display_name = anonymize_name(selected_submission['student_name'], selected_submission['student_id'])
        st.subheader(f"📊 {display_name}")
        
        # Create scrollable container for right panel
        with st.container(height=800):
            # Tabbed interface for detailed review
            tab1, tab2, tab3 = st.tabs(["📊 AI Feedback", "📓 Notebook", "✏️ Human Review"])
        
        with tab1:
            # AI Feedback tab
            st.subheader("AI-Generated Feedback")
            
            # Score metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("AI Score", f"{selected_submission['ai_score']}/37.5")
            with col2:
                st.metric("Percentage", f"{selected_submission['ai_percentage']:.1f}%")
            with col3:
                st.metric("Method", selected_submission['grading_method'] or "Unknown")
            
            # Scrollable container for feedback - same approach as notebook
            with st.container():
                st.markdown('<div style="max-height: 2000px; overflow-y: auto;">', unsafe_allow_html=True)
                
                # Display comprehensive feedback
                if selected_submission['ai_feedback']:
                    try:
                        feedback_data = json.loads(selected_submission['ai_feedback'])
                        
                        # Check for comprehensive_feedback wrapper (from grading system)
                        if isinstance(feedback_data, dict) and 'comprehensive_feedback' in feedback_data:
                            feedback_data = feedback_data['comprehensive_feedback']
                        
                        # Display instructor comments first if available
                        if isinstance(feedback_data, dict) and 'instructor_comments' in feedback_data:
                            st.markdown("**Overall Assessment:**")
                            st.info(feedback_data['instructor_comments'])
                            st.markdown("---")
                        
                        # Display structured feedback
                        if isinstance(feedback_data, dict) and 'detailed_feedback' in feedback_data:
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
                                        if isinstance(detailed[key], list):
                                            for item in detailed[key]:
                                                st.write(f"• {item}")
                                        else:
                                            st.write(detailed[key])
                        
                        # If it's a simple dict without structure, display all key-value pairs
                        elif isinstance(feedback_data, dict):
                            for key, value in feedback_data.items():
                                if key != 'instructor_comments':  # Already displayed above
                                    st.markdown(f"**{key.replace('_', ' ').title()}:**")
                                    if isinstance(value, list):
                                        for item in value:
                                            st.write(f"• {item}")
                                    else:
                                        st.write(value)
                                    st.markdown("---")
                        
                        # If it's a list, display items
                        elif isinstance(feedback_data, list):
                            for item in feedback_data:
                                st.write(f"• {item}")
                        
                        # Otherwise show as text
                        else:
                            st.write(str(feedback_data))
                    
                    except json.JSONDecodeError:
                        # Not JSON, display as plain text
                        st.markdown("**AI Feedback:**")
                        st.text_area("", selected_submission['ai_feedback'], height=400, disabled=True, label_visibility="collapsed")
                    except Exception as e:
                        st.error(f"Error displaying feedback: {e}")
                        st.text_area("Raw Feedback", selected_submission['ai_feedback'], height=200, disabled=True)
                else:
                    st.info("No AI feedback available for this submission")
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            # Notebook tab - same display as review page
            st.subheader("Student Notebook")
            
            # Display notebook with full HTML rendering - LONGER VIEW
            if selected_submission['notebook_path']:
                display_notebook_with_outputs(selected_submission['notebook_path'])
            else:
                st.warning("No notebook file associated with this submission")
        
        with tab3:
            # Human Review tab
            st.subheader("Human Review")
            
            # Get existing human feedback
            existing_feedback = training.get_human_feedback(selected_submission['id'])
            
            with st.form("human_review_form"):
                # Score input
                human_score = st.number_input(
                    "Human Score (0-37.5)",
                    min_value=0.0,
                    max_value=37.5,
                    value=float(existing_feedback['score'] if existing_feedback else selected_submission['ai_score']),
                    step=0.5
                )
                
                # Feedback templates
                template_options = [
                    "Custom",
                    "Excellent work! Shows strong understanding and complete execution.",
                    "Good effort with solid fundamentals. Some areas for improvement noted.",
                    "Needs review - missing key components or significant issues identified.",
                    "Incomplete submission - please address missing sections."
                ]
                
                template = st.selectbox("Quick Templates", template_options)
                
                # Feedback text area
                if existing_feedback and template == "Custom":
                    default_feedback = existing_feedback['feedback']
                elif template != "Custom":
                    default_feedback = template
                else:
                    default_feedback = ""
                
                human_feedback_text = st.text_area(
                    "Detailed Human Feedback",
                    value=default_feedback,
                    height=200
                )
                
                # Submit buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.form_submit_button("💾 Save Review", type="primary"):
                        if training.save_human_feedback(selected_submission['id'], human_score, human_feedback_text):
                            st.success("Human review saved successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to save review")
                
                with col2:
                    if st.form_submit_button("📄 Generate PDF"):
                        # Generate individual PDF report
                        try:
                            # This would integrate with existing PDF generation
                            st.info("PDF generation would be implemented here")
                        except Exception as e:
                            st.error(f"PDF generation error: {e}")
                
                with col3:
                    if st.form_submit_button("➡️ Next Student"):
                        # Move to next student
                        current_idx = next(i for i, s in enumerate(submissions) if s['id'] == selected_submission['id'])
                        next_idx = (current_idx + 1) % len(submissions)
                        st.session_state.selected_submission_id = submissions[next_idx]['id']
                        st.rerun()
            
            # Show existing review info
            if existing_feedback:
                st.info(f"Last updated: {existing_feedback['last_updated']} by {existing_feedback['instructor_id']}")
    
    # Bulk operations at the top
    st.markdown("---")
    st.subheader("📊 Bulk Operations & Reports")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📁 Print All Individual PDFs", type="primary", use_container_width=True):
            with st.spinner("Generating PDF reports for all submissions..."):
                pdf_files = []
                progress_bar = st.progress(0)
                
                for idx, submission in enumerate(submissions):
                    try:
                        # Use SAME logic as review page
                        from report_generator import PDFReportGenerator
                        report_gen = PDFReportGenerator()
                        
                        # Get submission data
                        conn = training.get_database_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM submissions WHERE id = ?", (submission['id'],))
                        sub_data = cursor.fetchone()
                        conn.close()
                        
                        if sub_data and sub_data['ai_feedback']:
                            try:
                                analysis_result = json.loads(sub_data['ai_feedback'])
                                # Keep full comprehensive_feedback - report generator will format it
                            except:
                                analysis_result = {}
                        else:
                            analysis_result = {}
                        
                        analysis_result['total_score'] = submission['ai_score']
                        analysis_result['max_score'] = 37.5
                        
                        display_name = anonymize_name(submission['student_name'], submission['student_id'])
                        pdf_path = report_gen.generate_report(
                            student_name=display_name,
                            assignment_id=selected_assignment['title'],
                            analysis_result=analysis_result
                        )
                        if pdf_path and os.path.exists(pdf_path):
                            pdf_files.append((display_name, pdf_path))
                        progress_bar.progress((idx + 1) / len(submissions))
                    except Exception as e:
                        st.warning(f"Failed to generate PDF for {display_name}: {e}")
                
                progress_bar.empty()
                
                if pdf_files:
                    # Create a zip file with all PDFs
                    zip_path = tempfile.mktemp(suffix='.zip')
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for student_name, pdf_path in pdf_files:
                            safe_name = "".join(c for c in student_name if c.isalnum() or c in (' ', '-', '_'))
                            zipf.write(pdf_path, f"{safe_name}_report.pdf")
                    
                    # Provide download button
                    with open(zip_path, 'rb') as f:
                        st.download_button(
                            "📥 Download All PDFs (ZIP)",
                            f.read(),
                            file_name=f"{selected_assignment['title']}_all_reports.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                    
                    st.success(f"Generated {len(pdf_files)} PDF reports!")
                    
                    # Clean up
                    os.unlink(zip_path)
                    for _, pdf_path in pdf_files:
                        try:
                            os.unlink(pdf_path)
                        except:
                            pass
                else:
                    st.error("No PDF reports were generated")
    
    with col2:
        if st.button("📊 Export to CSV", type="secondary", use_container_width=True):
            csv_data = []
            for submission in submissions:
                display_name = anonymize_name(submission['student_name'], submission['student_id'])
                display_id = anonymize_student_id(submission['student_id'])
                csv_data.append({
                    'Student Name': display_name,
                    'Student ID': display_id,
                    'Assignment': selected_assignment['title'],
                    'AI Score': submission['ai_score'],
                    'Human Score': submission['human_score'] if submission['human_score'] else '',
                    'Final Score': submission['final_score'],
                    'Max Score': 37.5,
                    'AI Percentage': f"{submission['ai_percentage']:.1f}%",
                    'Final Percentage': f"{(submission['final_score'] / 37.5 * 100):.1f}%",
                    'Status': submission['score_status'],
                    'Grade': submission['grade_category'],
                    'Submission Date': submission['submission_date'],
                    'Review Date': submission['review_date'] if submission['review_date'] else '',
                    'Grading Method': submission['grading_method'] if submission['grading_method'] else ''
                })
            
            df = pd.DataFrame(csv_data)
            csv_string = df.to_csv(index=False)
            
            st.download_button(
                "📥 Download CSV",
                csv_string,
                file_name=f"{selected_assignment['title']}_grades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.success(f"CSV ready with {len(csv_data)} submissions!")
    
    with col3:
        if st.button("📈 Training Report", type="secondary", use_container_width=True):
            st.markdown("### Training Summary Report")
            st.write(f"**Assignment:** {selected_assignment['title']}")
            st.write(f"**Total Submissions:** {stats['total_submissions']}")
            st.write(f"**Human Reviewed:** {stats['human_reviewed']} ({stats['review_percentage']}%)")
            st.write(f"**AI Accuracy:** {stats['ai_accuracy_percentage']}%")
            st.write(f"**Average Score Difference:** {stats['avg_score_difference']}")
            
            st.markdown("**Score Distribution:**")
            for category, count in stats['score_distribution'].items():
                st.write(f"• {category}: {count} students")

if __name__ == "__main__":
    enhanced_training_page()