import streamlit as st
import pandas as pd
import sqlite3
import nbformat
import json
import re
from nbconvert import HTMLExporter
import os
from datetime import datetime
from report_generator import PDFReportGenerator
from anonymization_utils import anonymize_name, anonymize_student_id

def parse_old_feedback_format(feedback_list):
    """Parse old feedback format (list of strings) into structured data"""
    result = {
        'element_scores': {},
        'code_issues': [],
        'question_analysis': {},
        'detailed_feedback': [],
        'overall_assessment': '',
        'code_fixes': []
    }
    
    # Extract scores and organize content
    for item in feedback_list:
        if isinstance(item, str):
            # Extract element scores with better parsing
            if 'Working Directory' in item and 'points' in item:
                score_match = re.search(r'\((\d+\.?\d*)/(\d+\.?\d*) points\)', item)
                if score_match:
                    result['element_scores']['working_directory'] = float(score_match.group(1))
                result['detailed_feedback'].append(item)
            
            elif 'Package Loading' in item and 'points' in item:
                score_match = re.search(r'\((\d+\.?\d*)/(\d+\.?\d*) points\)', item)
                if score_match:
                    result['element_scores']['package_loading'] = float(score_match.group(1))
                result['detailed_feedback'].append(item)
            
            elif ('CSV Import' in item or 'Excel Import' in item) and 'points' in item:
                score_match = re.search(r'\((\d+\.?\d*)/(\d+\.?\d*) points\)', item)
                if score_match:
                    if 'CSV' in item:
                        result['element_scores']['csv_import'] = float(score_match.group(1))
                    elif 'Excel' in item:
                        result['element_scores']['excel_import'] = float(score_match.group(1))
                result['detailed_feedback'].append(item)
            
            elif 'Data Inspection' in item and 'points' in item:
                score_match = re.search(r'\((\d+\.?\d*)/(\d+\.?\d*) points\)', item)
                if score_match:
                    result['element_scores']['data_inspection'] = float(score_match.group(1))
                result['detailed_feedback'].append(item)
            
            elif 'Reflection Questions' in item and 'points' in item:
                score_match = re.search(r'\((\d+\.?\d*)/(\d+\.?\d*) points\)', item)
                if score_match:
                    result['element_scores']['reflection_questions'] = float(score_match.group(1))
                result['detailed_feedback'].append(item)
            
            # Extract code issues
            elif 'ERROR:' in item:
                result['code_issues'].append(item)
            
            # Extract code fixes (the detailed R code solutions)
            elif '🔧' in item and ('```r' in item or 'Fix' in item):
                result['code_fixes'].append(item)
            
            # Extract overall assessment (this contains the code fixes)
            elif any(phrase in item for phrase in ['Good Job!', 'Excellent Work!', 'Keep Working!', 'Strong work!']):
                result['overall_assessment'] = item
                # Also add to code_fixes if it contains code solutions
                if '🔧' in item:
                    result['code_fixes'].append(item)
            
            # Extract reflection question details
            elif 'Data Types Analysis' in item:
                # Parse detailed reflection feedback
                score_match = re.search(r'\((\d+\.?\d*)/(\d+\.?\d*) points\)', item)
                if score_match:
                    result['question_analysis']['data_types'] = {
                        'score': float(score_match.group(1)), 
                        'max_score': float(score_match.group(2)), 
                        'quality': 'Good',
                        'detailed_feedback': item
                    }
            
            elif 'Data Quality Assessment' in item:
                score_match = re.search(r'\((\d+\.?\d*)/(\d+\.?\d*) points\)', item)
                if score_match:
                    result['question_analysis']['data_quality'] = {
                        'score': float(score_match.group(1)), 
                        'max_score': float(score_match.group(2)), 
                        'quality': 'Good',
                        'detailed_feedback': item
                    }
            
            elif 'Analysis Readiness' in item:
                score_match = re.search(r'\((\d+\.?\d*)/(\d+\.?\d*) points\)', item)
                if score_match:
                    result['question_analysis']['analysis_readiness'] = {
                        'score': float(score_match.group(1)), 
                        'max_score': float(score_match.group(2)), 
                        'quality': 'Satisfactory',
                        'detailed_feedback': item
                    }
    
    # Parse summary scores from REFLECTION QUESTIONS ANALYSIS section
    for item in feedback_list:
        if isinstance(item, str):
            if 'Data Types: Excellent' in item:
                match = re.search(r'Data Types: (\w+) \((\d+\.?\d*)/(\d+\.?\d*) points\)', item)
                if match:
                    result['question_analysis']['data_types'] = {
                        'score': float(match.group(2)), 
                        'max_score': float(match.group(3)), 
                        'quality': match.group(1)
                    }
            elif 'Data Quality: Excellent' in item:
                match = re.search(r'Data Quality: (\w+) \((\d+\.?\d*)/(\d+\.?\d*) points\)', item)
                if match:
                    result['question_analysis']['data_quality'] = {
                        'score': float(match.group(2)), 
                        'max_score': float(match.group(3)), 
                        'quality': match.group(1)
                    }
            elif 'Analysis Readiness: Satisfactory' in item:
                match = re.search(r'Analysis Readiness: (\w+) \((\d+\.?\d*)/(\d+\.?\d*) points\)', item)
                if match:
                    result['question_analysis']['analysis_readiness'] = {
                        'score': float(match.group(2)), 
                        'max_score': float(match.group(3)), 
                        'quality': match.group(1)
                    }
    
    return result

def extract_name_from_path(notebook_path: str) -> str:
    """Extract student name from notebook file path"""
    if not notebook_path:
        return None
    
    try:
        from pathlib import Path
        from assignment_manager import parse_github_classroom_filename
        
        filename = Path(notebook_path).stem
        parsed_info = parse_github_classroom_filename(filename)
        return parsed_info.get('name')
    except:
        return None

def create_assignment_zip(grader, assignment_id: int, assignment_name: str):
    """Create a zip file of all reports for an assignment and offer download"""
    try:
        import zipfile
        import tempfile
        from pathlib import Path
        
        # Clean assignment name for folder
        clean_assignment = re.sub(r'[^\w\s-]', '', assignment_name).replace(' ', '_')
        assignment_folder = os.path.join("reports", clean_assignment)
        
        if not os.path.exists(assignment_folder):
            st.error(f"No reports found for {assignment_name}. Generate reports first.")
            return
        
        # Count PDF files
        pdf_files = list(Path(assignment_folder).glob("*.pdf"))
        if not pdf_files:
            st.error(f"No PDF reports found in {assignment_name} folder.")
            return
        
        # Create zip file
        zip_filename = f"{clean_assignment}_Reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join("reports", zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for pdf_file in pdf_files:
                zipf.write(pdf_file, pdf_file.name)
        
        # Offer download
        with open(zip_path, 'rb') as f:
            st.download_button(
                label=f"📥 Download {assignment_name} Reports ({len(pdf_files)} files)",
                data=f.read(),
                file_name=zip_filename,
                mime="application/zip",
                key=f"download_zip_{assignment_id}"
            )
        
        st.success(f"✅ Created zip file with {len(pdf_files)} reports!")
        
        # Clean up zip file after a delay (optional)
        # os.remove(zip_path)  # Uncomment if you want to auto-delete
        
    except Exception as e:
        st.error(f"Error creating zip file: {str(e)}")
        import traceback
        st.error(f"Details: {traceback.format_exc()}")

def view_results_page(grader):
    st.header("👀 Quick View")
    st.caption("Read-only view of graded submissions")
    
    # Select assignment
    conn = sqlite3.connect(grader.db_path)
    assignments = pd.read_sql_query("SELECT id, name FROM assignments ORDER BY created_date DESC", conn)
    
    if assignments.empty:
        st.warning("No assignments found.")
        conn.close()
        return
    
    assignment_options = {row['name']: row['id'] for _, row in assignments.iterrows()}
    selected_assignment_name = st.selectbox("Select Assignment", list(assignment_options.keys()))
    assignment_id = assignment_options[selected_assignment_name]
    
    # Get submissions for this assignment
    submissions = pd.read_sql_query("""
        SELECT s.*, st.name as student_name, st.student_id as student_identifier
        FROM submissions s
        LEFT JOIN students st ON s.student_id = st.id
        WHERE s.assignment_id = ?
        ORDER BY s.submission_date DESC
    """, conn, params=(assignment_id,))
    
    conn.close()
    
    if submissions.empty:
        st.info("No submissions found for this assignment.")
        return
    
    # Display summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Submissions", len(submissions))
    
    with col2:
        graded_count = len(submissions[submissions['final_score'].notna()])
        st.metric("Graded", graded_count)
    
    with col3:
        if graded_count > 0:
            avg_score = submissions[submissions['final_score'].notna()]['final_score'].mean()
            st.metric("Average Score", f"{avg_score:.1f}")
        else:
            st.metric("Average Score", "N/A")
    
    with col4:
        ai_graded = len(submissions[submissions['ai_score'].notna()])
        st.metric("AI Graded", ai_graded)
    
    # Initialize session state for selected submission
    if 'quick_view_selected_id' not in st.session_state:
        st.session_state.quick_view_selected_id = submissions.iloc[0]['id'] if not submissions.empty else None
    
    # Dual panel layout: Left 1/3, Right 2/3
    left_col, right_col = st.columns([1, 2])
    
    with left_col:
        st.subheader("📋 Submissions")
        
        # Scrollable container for student list
        with st.container(height=800):
            for _, submission in submissions.iterrows():
                with st.container():
                    is_selected = submission['id'] == st.session_state.quick_view_selected_id
                    button_type = "primary" if is_selected else "secondary"
                    
                    # Get display name
                    student_name = submission['student_name'] if submission['student_name'] else f"Student {submission['student_identifier']}"
                    display_name = anonymize_name(student_name, submission['student_identifier'])
                    
                    # Grade indicator
                    final_score = submission['final_score'] if pd.notna(submission['final_score']) else 0
                    if final_score >= 35:
                        grade_indicator = "🎉"
                    elif final_score >= 30:
                        grade_indicator = "👍"
                    elif final_score >= 25:
                        grade_indicator = "⚠️"
                    elif final_score > 0:
                        grade_indicator = "❌"
                    else:
                        grade_indicator = "⏳"
                    
                    if st.button(
                        f"{grade_indicator} {display_name} ({final_score:.1f})",
                        key=f"quick_view_{submission['id']}",
                        type=button_type,
                        use_container_width=True
                    ):
                        st.session_state.quick_view_selected_id = submission['id']
                        st.rerun()
                    
                    # Add spacing
                    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    
    with right_col:
        # Get selected submission
        selected_submission = submissions[submissions['id'] == st.session_state.quick_view_selected_id].iloc[0]
        student_name = selected_submission['student_name'] if selected_submission['student_name'] else f"Student {selected_submission['student_identifier']}"
        display_name = anonymize_name(student_name, selected_submission['student_identifier'])
        
        st.subheader(f"📊 {display_name}")
        
        # Tabs for notebook and feedback
        tab1, tab2 = st.tabs(["📓 Notebook", "📊 AI Feedback"])
        
        with tab1:
            # Display notebook
            if selected_submission['notebook_path'] and os.path.exists(selected_submission['notebook_path']):
                try:
                    with open(selected_submission['notebook_path'], 'r', encoding='utf-8') as f:
                        nb = nbformat.read(f, as_version=4)
                    
                    html_exporter = HTMLExporter()
                    html_exporter.template_name = 'classic'
                    (body, resources) = html_exporter.from_notebook_node(nb)
                    
                    st.components.v1.html(body, height=800, scrolling=True)
                except Exception as e:
                    st.error(f"Error displaying notebook: {e}")
            else:
                st.warning("Notebook not found")
        
        with tab2:
            # Display AI feedback
            if pd.notna(selected_submission['ai_feedback']):
                try:
                    feedback = json.loads(selected_submission['ai_feedback'])
                    
                    # Score display
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("AI Score", f"{selected_submission['ai_score']:.1f}/37.5")
                    with col2:
                        if pd.notna(selected_submission['final_score']):
                            st.metric("Final Score", f"{selected_submission['final_score']:.1f}/37.5")
                    
                    # Display feedback
                    if 'comprehensive_feedback' in feedback:
                        comp_feed = feedback['comprehensive_feedback']
                        if isinstance(comp_feed, dict) and 'instructor_comments' in comp_feed:
                            st.markdown("**Instructor Assessment:**")
                            st.info(comp_feed['instructor_comments'])
                    
                    st.markdown("---")
                    st.caption("This is a read-only view. Use 'Review & Grade' to edit scores.")
                    
                except Exception as e:
                    st.error(f"Error parsing feedback: {e}")
            else:
                st.info("No AI feedback available")


def old_view_results_page_backup(grader):
    """Old implementation - kept for reference"""
    # Management options
    pass
    
    if False:  # Disabled old code
                generate_student_reports_interface(grader, assignment_id, selected_assignment)
                st.session_state.generate_all_reports = False
    
    # Individual student report selection
    if not submissions.empty:
        st.subheader("📝 Individual Reports")
        
        # Filter to graded submissions only
        graded_submissions = submissions[submissions['ai_score'].notna()]
        
        if not graded_submissions.empty:
            col_select1, col_select2 = st.columns([3, 1])
            
            with col_select1:
                # Create student options
                student_options = []
                for _, row in graded_submissions.iterrows():
                    student_name = row['student_name'] if row['student_name'] != 'Unknown' else f"Student_{row['student_id']}"
                    display_name = anonymize_name(student_name, row['student_id'])
                    student_options.append(f"{display_name} (Score: {row['ai_score']:.1f})")
                
                selected_student = st.selectbox(
                    "Select student for individual report:",
                    student_options,
                    key="individual_report_select"
                )
            
            with col_select2:
                st.write("")  # Spacing
                if st.button("📝 Generate Report", key="generate_individual"):
                    # Find the selected submission
                    selected_index = student_options.index(selected_student)
                    selected_submission = graded_submissions.iloc[selected_index]
                    generate_individual_report(grader, selected_submission, selected_assignment)
        else:
            st.info("No graded submissions available for report generation.")
    
    st.markdown("---")
    
    # Prepare display data
    display_data = submissions.copy()
    display_data['student_display'] = display_data.apply(
        lambda row: f"{row['student_name']} ({row['student_id']})" if row['student_name'] else row['student_id'],
        axis=1
    )
    
    # Select columns to display
    display_columns = ['student_display', 'submission_date', 'ai_score', 'human_score', 'final_score']
    display_data = display_data[display_columns].rename(columns={
        'student_display': 'Student',
        'submission_date': 'Submitted',
        'ai_score': 'AI Score',
        'human_score': 'Human Score',
        'final_score': 'Final Score'
    })
    
    # Pagination and filtering
    items_per_page = 10
    total_items = len(submissions)
    total_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1
    
    col_page1, col_page2, col_page3 = st.columns([1, 2, 1])
    
    with col_page1:
        current_page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, key="results_page")
    
    with col_page2:
        # Filter options
        filter_option = st.selectbox("Filter by:", ["All", "Graded", "Ungraded", "High Scores (>30)", "Low Scores (<20)"])
    
    with col_page3:
        st.write(f"Showing {total_items} submissions")
    
    # Apply filters
    filtered_submissions = submissions.copy()
    
    if filter_option == "Graded":
        filtered_submissions = filtered_submissions[filtered_submissions['ai_score'].notna()]
    elif filter_option == "Ungraded":
        filtered_submissions = filtered_submissions[filtered_submissions['ai_score'].isna()]
    elif filter_option == "High Scores (>30)":
        filtered_submissions = filtered_submissions[filtered_submissions['ai_score'] > 30]
    elif filter_option == "Low Scores (<20)":
        filtered_submissions = filtered_submissions[filtered_submissions['ai_score'] < 20]
    
    # Pagination
    start_idx = (current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_submissions = filtered_submissions.iloc[start_idx:end_idx]
    
    if page_submissions.empty:
        st.info("No submissions match the current filter.")
        return
    
    # Display submissions in a more compact table format
    st.subheader(f"Page {current_page} of {total_pages}")
    
    # Create a more organized display
    for idx, row in page_submissions.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            
            with col1:
                # Better student name display
                student_name = "Unknown Student"
                if row['student_name'] and row['student_name'] != 'Unknown':
                    student_name = row['student_name']
                elif row['student_id']:
                    student_name = f"Student {row['student_id']}"
                
                # Apply anonymization
                display_name = anonymize_name(student_name, row['student_id'])
                
                st.write(f"**{display_name}**")
                st.caption(f"Submitted: {row['submission_date']}")
            
            with col2:
                # Score display with color coding
                if pd.notna(row['ai_score']):
                    score = row['ai_score']
                    if score >= 30:
                        st.success(f"Score: {score:.1f}/37.5")
                    elif score >= 20:
                        st.warning(f"Score: {score:.1f}/37.5")
                    else:
                        st.error(f"Score: {score:.1f}/37.5")
                else:
                    st.info("Not graded yet")
            
            with col3:
                if st.button("👁️ View", key=f"view_{row['id']}", help="View submission details"):
                    st.session_state.current_submission = row['id']
                    st.session_state.page = "view_submission"
            
            with col4:
                if pd.notna(row['ai_score']):
                    if st.button("📝 Report", key=f"report_{row['id']}", help="Generate PDF report"):
                        generate_individual_report(grader, row, selected_assignment)
                else:
                    if st.button("⚡ Grade", key=f"grade_{row['id']}", help="Grade this submission"):
                        st.session_state.current_submission = row['id']
                        st.session_state.page = "manual_grade"
        
        st.divider()
    
    # Export and report options
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Results to CSV"):
            try:
                # Get enhanced data with proper student information
                conn_temp = sqlite3.connect(grader.db_path)
                enhanced_data = pd.read_sql_query("""
                    SELECT s.*, 
                           COALESCE(st.name, 'Unknown') as student_name,
                           st.student_id as student_id_number
                    FROM submissions s
                    LEFT JOIN students st ON s.student_id = st.id
                    WHERE s.assignment_id = ?
                    ORDER BY st.student_id
                """, conn_temp, params=(assignment_id,))
                conn_temp.close()
                
                if enhanced_data.empty:
                    st.warning("No submissions found for export.")
                    return
                
                # Clean and validate student names
                def clean_student_name(row):
                    name = row['student_name']
                    student_id = row['student_id_number']
                    notebook_path = row.get('notebook_path', '')
                    
                    # Handle malformed names (like "** [YOUR NAME HERE")
                    if pd.isna(name) or name == 'Unknown' or '**' in str(name) or '[YOUR NAME HERE' in str(name):
                        # Try to extract from filename first
                        if notebook_path:
                            try:
                                from pathlib import Path
                                filename = Path(notebook_path).stem
                                extracted_name = extract_name_from_path(notebook_path)
                                if extracted_name and extracted_name != 'Unknown':
                                    return extracted_name
                            except:
                                pass
                        # Fallback to student ID
                        return f"Student_{student_id}" if student_id else "Unknown_Student"
                    
                    return str(name).strip()
                
                # Apply name cleaning
                enhanced_data['cleaned_student_name'] = enhanced_data.apply(clean_student_name, axis=1)
                
                # Handle missing scores (replace NaN with appropriate values)
                enhanced_data['ai_score'] = enhanced_data['ai_score'].fillna(0).round(2)
                enhanced_data['human_score'] = enhanced_data['human_score'].fillna('')
                enhanced_data['final_score'] = enhanced_data['final_score'].fillna(enhanced_data['ai_score']).round(2)
                
                # Format submission date for better readability
                enhanced_data['submission_date'] = pd.to_datetime(enhanced_data['submission_date']).dt.strftime('%Y-%m-%d %H:%M')
                
                # Create final export with clean data
                final_export = enhanced_data[[
                    'student_id_number', 'cleaned_student_name', 'ai_score', 'human_score', 'final_score', 'submission_date'
                ]].rename(columns={
                    'student_id_number': 'Student ID',
                    'cleaned_student_name': 'Student Name',
                    'ai_score': 'AI Score', 
                    'human_score': 'Manual Score',
                    'final_score': 'Final Score',
                    'submission_date': 'Submission Date'
                })
                
                # Sort by Student ID for easier reading and gradebook import
                final_export = final_export.sort_values('Student ID')
                
                # Generate CSV
                csv = final_export.to_csv(index=False)
                
                # Show export statistics
                graded_count = len(final_export[final_export['AI Score'] > 0])
                avg_score = final_export[final_export['AI Score'] > 0]['AI Score'].mean() if graded_count > 0 else 0
                
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Total Students", len(final_export))
                with col_stat2:
                    st.metric("Graded", graded_count)
                with col_stat3:
                    st.metric("Average Score", f"{avg_score:.1f}/37.5" if graded_count > 0 else "N/A")
                
                # Show preview
                st.write("**Export Preview:**")
                st.dataframe(final_export.head(10), use_container_width=True)
                
                # Download button
                st.download_button(
                    label=f"📊 Download Gradebook CSV ({len(final_export)} students)",
                    data=csv,
                    file_name=f"{selected_assignment}_gradebook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key=f"csv_export_{assignment_id}"
                )
                
                st.success(f"✅ CSV export ready with {len(final_export)} student records!")
                
            except Exception as e:
                st.error(f"Error creating CSV export: {str(e)}")
                import traceback
                st.error(f"Details: {traceback.format_exc()}")
    
    with col2:
        if st.button("📝 Generate Individual Reports"):
            generate_student_reports_interface(grader, assignment_id, selected_assignment)
    
    conn.close()
    
    # Handle page navigation
    if st.session_state.get('page') == 'view_submission':
        view_submission_detail(grader)
    elif st.session_state.get('page') == 'manual_grade':
        manual_grading_interface(grader)

def generate_student_reports_interface(grader, assignment_id: int, assignment_name: str):
    """Interface for generating student reports"""
    
    st.subheader("📝 Generate Individual Student Reports")
    
    if st.button("Generate PDF Reports for All Students"):
        with st.spinner("Generating detailed PDF reports for all students..."):
            try:
                report_generator = PDFReportGenerator()
                
                # Get all graded submissions for this assignment
                conn = sqlite3.connect(grader.db_path)
                submissions = pd.read_sql_query("""
                    SELECT s.*, 
                           COALESCE(st.name, 'Unknown') as student_name, 
                           COALESCE(st.student_id, 'Unknown') as student_id
                    FROM submissions s
                    LEFT JOIN students st ON s.student_id = st.id
                    WHERE s.assignment_id = ? AND s.ai_score IS NOT NULL
                """, conn, params=(assignment_id,))
                conn.close()
                
                if submissions.empty:
                    st.warning("No graded submissions found for this assignment.")
                    return
                
                generated_reports = []
                
                for _, submission in submissions.iterrows():
                    try:
                        # Parse the FULL AI feedback structure (SAME as individual report)
                        if submission['ai_feedback']:
                            try:
                                analysis_result = json.loads(submission['ai_feedback'])
                                
                                # Ensure it has the required structure
                                if not isinstance(analysis_result, dict):
                                    analysis_result = {'comprehensive_feedback': {}}
                                
                                # Keep the full comprehensive_feedback including detailed_feedback
                                # The report generator will handle formatting and filtering
                                
                            except Exception as e:
                                print(f"Error parsing feedback: {e}")
                                analysis_result = {}
                        else:
                            analysis_result = {}
                        
                        analysis_result['total_score'] = submission['ai_score']
                        analysis_result['max_score'] = 37.5
                        
                        # Clean student name for report generation
                        student_name = submission['student_name'] or f"Student_{submission['student_id']}"
                        # Clean problematic characters from student name
                        student_name = re.sub(r'[*\[\]<>:"/\\|?]', '', student_name).strip()
                        if not student_name:
                            student_name = f"Student_{submission['student_id']}"
                        
                        # Generate PDF report
                        report_path = report_generator.generate_report(
                            student_name=student_name,
                            assignment_id=assignment_name,
                            analysis_result=analysis_result
                        )
                        
                        generated_reports.append({
                            'student': student_name,
                            'path': report_path
                        })
                        
                    except Exception as e:
                        st.error(f"Failed to generate report for student {submission.get('student_name', 'Unknown')}: {str(e)}")
                        continue
                
                if generated_reports:
                    st.success(f"✅ Generated reports for {len(generated_reports)} students!")
                    
                    # Show report details
                    st.write("**Generated Reports:**")
                    
                    for report in generated_reports:
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"📚 **{report['student']}**")
                        
                        with col2:
                            with open(report['path'], 'rb') as f:
                                st.download_button(
                                    label="📝 Download Report",
                                    data=f.read(),
                                    file_name=f"{report['student']}_feedback.pdf",
                                    mime="application/pdf",
                                    key=f"docx_{report['student']}"
                                )
                    
                    # Bulk download option
                    st.write("---")
                    st.info("💡 **Tip:** Reports are saved in the `reports/` folder. You can zip this folder to share all reports at once.")
                    
            except Exception as e:
                st.error(f"Error generating reports: {str(e)}")
                import traceback
                st.error(f"Details: {traceback.format_exc()}")

def generate_individual_report(grader, submission_row, assignment_name):
    """Generate a PDF report - SINGLE SOURCE OF TRUTH with all sections"""
    try:
        from report_generator import PDFReportGenerator
        
        report_generator = PDFReportGenerator()
        
        # Get student name
        student_name = submission_row.get('student_name')
        if pd.isna(student_name) or student_name == 'Unknown' or not student_name:
            # Try to extract name from the notebook filename
            notebook_path = submission_row.get('notebook_path', '')
            if notebook_path:
                from pathlib import Path
                from assignment_manager import parse_github_classroom_filename
                
                filename = Path(notebook_path).stem
                parsed_info = parse_github_classroom_filename(filename)
                student_name = parsed_info.get('name') or f"Student_{submission_row.get('student_id', 'Unknown')}"
            else:
                student_name = f"Student_{submission_row.get('student_id', 'Unknown')}"
        
        # Parse the FULL AI feedback structure
        if submission_row['ai_feedback']:
            try:
                analysis_result = json.loads(submission_row['ai_feedback'])
                
                # Ensure it has the required structure
                if not isinstance(analysis_result, dict):
                    analysis_result = {'comprehensive_feedback': {}}
                
                # Keep the full comprehensive_feedback including detailed_feedback
                # The report generator will handle formatting and converting to paragraphs
                
            except Exception as e:
                print(f"Error parsing feedback: {e}")
                analysis_result = {}
        else:
            analysis_result = {}
        
        # Ensure required fields
        analysis_result['total_score'] = submission_row['ai_score'] or 0
        analysis_result['max_score'] = 37.5
        
        # Generate report with all technical sections + short instructor feedback
        report_path = report_generator.generate_report(
            student_name=student_name,
            assignment_id=assignment_name,
            analysis_result=analysis_result
        )
        
        if not report_path:
            st.error("Failed to generate report")
            return
        
        # Show success and provide download
        st.success(f"✅ Report generated for {student_name}")
        st.info(f"📁 Report saved to: {report_path}")
        
        # Provide download button
        with open(report_path, 'rb') as f:
            st.download_button(
                label=f"📝 Download {student_name} Report",
                data=f.read(),
                file_name=f"{student_name}_{assignment_name}_report.pdf",
                mime="application/pdf",
                key=f"download_{submission_row['id']}"
            )
        
    except Exception as e:
        st.error(f"Error generating individual report: {str(e)}")
        import traceback
        st.error(f"Details: {traceback.format_exc()}")

def view_submission_detail(grader):
    st.header("📝 Submission Details")
    
    if 'current_submission' not in st.session_state:
        st.error("No submission selected.")
        return
    
    # Get submission details
    conn = sqlite3.connect(grader.db_path)
    submission = pd.read_sql_query("""
        SELECT s.*, st.name as student_name, a.name as assignment_name
        FROM submissions s
        LEFT JOIN students st ON s.student_id = st.id
        JOIN assignments a ON s.assignment_id = a.id
        WHERE s.id = ?
    """, conn, params=(st.session_state.current_submission,)).iloc[0]
    
    conn.close()
    
    # Display submission info
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Student:** {submission['student_name'] or submission['student_id']}")
        st.write(f"**Assignment:** {submission['assignment_name']}")
        st.write(f"**Submitted:** {submission['submission_date']}")
    
    with col2:
        if pd.notna(submission['ai_score']):
            st.write(f"**AI Score:** {submission['ai_score']:.1f}")
        if pd.notna(submission['human_score']):
            st.write(f"**Human Score:** {submission['human_score']:.1f}")
        if pd.notna(submission['final_score']):
            st.write(f"**Final Score:** {submission['final_score']:.1f}")
    
    # Display AI feedback if available
    if pd.notna(submission['ai_feedback']):
        st.subheader("AI Feedback")
        try:
            feedback_data = json.loads(submission['ai_feedback'])
            
            # Check if this is the new comprehensive feedback format
            if isinstance(feedback_data, dict) and 'comprehensive_feedback' in feedback_data:
                # Display comprehensive feedback from Business Analytics Grader
                comp_feedback = feedback_data['comprehensive_feedback']
                
                # Show instructor comments
                if 'instructor_comments' in comp_feedback:
                    st.write("**Overall Assessment:**")
                    st.write(comp_feedback['instructor_comments'])
                    st.write("---")
                
                # Show detailed feedback sections
                if 'detailed_feedback' in comp_feedback:
                    detailed = comp_feedback['detailed_feedback']
                    
                    # Reflection Assessment
                    if 'reflection_assessment' in detailed and detailed['reflection_assessment']:
                        st.write("**🤔 Reflection & Critical Thinking:**")
                        for item in detailed['reflection_assessment']:
                            st.write(f"• {item}")
                        st.write("")
                    
                    # Analytical Strengths
                    if 'analytical_strengths' in detailed and detailed['analytical_strengths']:
                        st.write("**💪 Analytical Strengths:**")
                        for item in detailed['analytical_strengths']:
                            st.write(f"• {item}")
                        st.write("")
                    
                    # Business Application
                    if 'business_application' in detailed and detailed['business_application']:
                        st.write("**💼 Business Application:**")
                        for item in detailed['business_application']:
                            st.write(f"• {item}")
                        st.write("")
                    
                    # Learning Demonstration
                    if 'learning_demonstration' in detailed and detailed['learning_demonstration']:
                        st.write("**📚 Learning Demonstration:**")
                        for item in detailed['learning_demonstration']:
                            st.write(f"• {item}")
                        st.write("")
                    
                    # Areas for Development
                    if 'areas_for_development' in detailed and detailed['areas_for_development']:
                        st.write("**🎯 Areas for Development:**")
                        for item in detailed['areas_for_development']:
                            st.write(f"• {item}")
                        st.write("")
                    
                    # Recommendations
                    if 'recommendations' in detailed and detailed['recommendations']:
                        st.write("**💡 Recommendations:**")
                        for item in detailed['recommendations']:
                            st.write(f"• {item}")
                        st.write("")
                
                # Show technical analysis in expander
                if 'technical_analysis' in feedback_data:
                    with st.expander("🔧 Technical Analysis Details"):
                        tech = feedback_data['technical_analysis']
                        
                        # Code Strengths
                        if 'code_strengths' in tech and tech['code_strengths']:
                            st.write("**Code Strengths:**")
                            for item in tech['code_strengths']:
                                st.write(f"• {item}")
                            st.write("")
                        
                        # Code Suggestions
                        if 'code_suggestions' in tech and tech['code_suggestions']:
                            st.write("**Code Suggestions:**")
                            for item in tech['code_suggestions']:
                                st.write(f"• {item}")
                            st.write("")
                        
                        # Technical Observations
                        if 'technical_observations' in tech and tech['technical_observations']:
                            st.write("**Technical Observations:**")
                            for item in tech['technical_observations']:
                                st.write(f"• {item}")
                            st.write("")
            
            elif isinstance(feedback_data, list):
                # Legacy format - display as list
                for item in feedback_data:
                    st.write(f"• {item}")
            
            else:
                # Unknown format - display raw
                st.json(feedback_data)
                
        except Exception as e:
            st.error(f"Error parsing feedback: {e}")
            st.write(submission['ai_feedback'])
    
    # Display human feedback if available
    if pd.notna(submission['human_feedback']):
        st.subheader("Human Feedback")
        st.write(submission['human_feedback'])
    
    # Display notebook
    st.subheader("Notebook Content")
    
    if os.path.exists(submission['notebook_path']):
        try:
            # Convert notebook to HTML for display
            with open(submission['notebook_path'], 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
            
            html_exporter = HTMLExporter()
            html_exporter.template_name = 'classic'
            (body, resources) = html_exporter.from_notebook_node(nb)
            
            # Display HTML
            st.components.v1.html(body, height=800, scrolling=True)
            
        except Exception as e:
            st.error(f"Error displaying notebook: {str(e)}")
            
            # Fallback: show raw content
            with open(submission['notebook_path'], 'r', encoding='utf-8') as f:
                content = f.read()
            st.code(content, language='json')
    else:
        st.error("Notebook file not found.")
    
    if st.button("Back to Results"):
        st.session_state.page = None
        st.rerun()

def manual_grading_interface(grader):
    st.header("✏️ Manual Grading")
    
    if 'current_submission' not in st.session_state:
        st.error("No submission selected.")
        return
    
    # Get submission details
    conn = sqlite3.connect(grader.db_path)
    submission = pd.read_sql_query("""
        SELECT s.*, st.name as student_name, a.name as assignment_name, a.rubric, a.total_points
        FROM submissions s
        LEFT JOIN students st ON s.student_id = st.student_id
        JOIN assignments a ON s.assignment_id = a.id
        WHERE s.id = ?
    """, conn, params=(st.session_state.current_submission,)).iloc[0]
    
    # Display submission info
    st.write(f"**Student:** {submission['student_name'] or submission['student_id']}")
    st.write(f"**Assignment:** {submission['assignment_name']}")
    
    # Show AI score and feedback for reference
    if pd.notna(submission['ai_score']):
        st.info(f"AI suggested score: {submission['ai_score']:.1f}")
        
        if pd.notna(submission['ai_feedback']):
            with st.expander("AI Feedback"):
                try:
                    feedback_data = json.loads(submission['ai_feedback'])
                    
                    # Check if this is comprehensive feedback format
                    if isinstance(feedback_data, dict) and 'comprehensive_feedback' in feedback_data:
                        comp_feedback = feedback_data['comprehensive_feedback']
                        
                        # Show instructor comments
                        if 'instructor_comments' in comp_feedback:
                            st.write("**Overall Assessment:**")
                            st.write(comp_feedback['instructor_comments'])
                        
                        # Show key detailed feedback sections (condensed for manual review)
                        if 'detailed_feedback' in comp_feedback:
                            detailed = comp_feedback['detailed_feedback']
                            
                            for section_name, items in detailed.items():
                                if items and isinstance(items, list):
                                    section_title = section_name.replace('_', ' ').title()
                                    st.write(f"**{section_title}:**")
                                    for item in items[:2]:  # Show first 2 items only
                                        st.write(f"• {item}")
                                    if len(items) > 2:
                                        st.write(f"... and {len(items) - 2} more items")
                                    st.write("")
                    
                    elif isinstance(feedback_data, list):
                        # Legacy format
                        for item in feedback_data:
                            st.write(f"• {item}")
                    
                    else:
                        st.json(feedback_data)
                        
                except Exception as e:
                    st.error(f"Error parsing feedback: {e}")
                    st.write(submission['ai_feedback'])
    
    # Display rubric
    if submission['rubric']:
        try:
            rubric = json.loads(submission['rubric'])
            st.subheader("Grading Rubric")
            
            total_rubric_points = 0
            rubric_scores = {}
            
            for criterion, details in rubric.items():
                points = details.get('points', 0)
                description = details.get('description', '')
                total_rubric_points += points
                
                st.write(f"**{criterion}** ({points} points): {description}")
                rubric_scores[criterion] = st.slider(
                    f"Score for {criterion}",
                    min_value=0,
                    max_value=points,
                    value=int(submission['human_score'] * points / submission['total_points']) if pd.notna(submission['human_score']) else points,
                    key=f"rubric_{criterion}"
                )
        except:
            rubric = {}
            total_rubric_points = submission['total_points']
    else:
        rubric = {}
        total_rubric_points = submission['total_points']
    
    # Manual scoring
    st.subheader("Manual Grading")
    
    if rubric:
        # Calculate score from rubric
        calculated_score = sum(rubric_scores.values())
        st.write(f"Calculated score from rubric: {calculated_score}/{total_rubric_points}")
        manual_score = calculated_score
    else:
        # Direct scoring
        manual_score = st.number_input(
            "Manual Score",
            min_value=0.0,
            max_value=float(submission['total_points']),
            value=float(submission['human_score']) if pd.notna(submission['human_score']) else 0.0,
            step=0.5
        )
    
    # Feedback
    current_feedback = submission['human_feedback'] if pd.notna(submission['human_feedback']) else ""
    feedback = st.text_area("Feedback", value=current_feedback, height=150)
    
    # Display notebook for reference
    with st.expander("View Notebook", expanded=False):
        if os.path.exists(submission['notebook_path']):
            try:
                with open(submission['notebook_path'], 'r', encoding='utf-8') as f:
                    nb = nbformat.read(f, as_version=4)
                
                html_exporter = HTMLExporter()
                html_exporter.template_name = 'classic'
                (body, resources) = html_exporter.from_notebook_node(nb)
                
                st.components.v1.html(body, height=600, scrolling=True)
                
            except Exception as e:
                st.error(f"Error displaying notebook: {str(e)}")
    
    # Save grading
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Save Grade"):
            # Calculate final score (blend of AI and human if both exist)
            if pd.notna(submission['ai_score']):
                final_score = 0.3 * submission['ai_score'] + 0.7 * manual_score
            else:
                final_score = manual_score
            
            # Update database
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE submissions
                SET human_score = ?, human_feedback = ?, final_score = ?, graded_date = ?
                WHERE id = ?
            """, (manual_score, feedback, final_score, datetime.now(), submission['id']))
            
            # Update training data
            cursor.execute("""
                UPDATE ai_training_data
                SET human_score = ?, human_feedback = ?
                WHERE assignment_id = ? AND cell_content = ?
            """, (manual_score, feedback, submission['assignment_id'], submission['notebook_path']))
            
            conn.commit()
            st.success("Grade saved successfully!")
    
    with col2:
        if st.button("Back to Results"):
            st.session_state.page = None
            st.rerun()
    
    conn.close()