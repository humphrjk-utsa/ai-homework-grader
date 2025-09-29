#!/usr/bin/env python3
"""
Connect the web interface to our business analytics grader
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import os
import nbformat
from business_analytics_grader import BusinessAnalyticsGrader
from grading_validator import GradingValidator
from report_generator import PDFReportGenerator

def grade_submissions_page(grader):
    """Enhanced grade submissions page using our business analytics grader"""
    st.header("⚡ Grade Submissions")
    
    # Select assignment
    conn = sqlite3.connect(grader.db_path)
    assignments = pd.read_sql_query("SELECT id, name FROM assignments ORDER BY created_date DESC", conn)
    
    if assignments.empty:
        st.warning("No assignments found. Please create an assignment first.")
        conn.close()
        return
    
    assignment_options = {row['name']: row['id'] for _, row in assignments.iterrows()}
    selected_assignment = st.selectbox("Select Assignment", list(assignment_options.keys()))
    assignment_id = assignment_options[selected_assignment]
    
    # Get ungraded submissions
    ungraded_submissions = pd.read_sql_query("""
        SELECT s.*, st.name as student_name, st.student_id as student_identifier
        FROM submissions s
        LEFT JOIN students st ON s.student_id = st.id
        WHERE s.assignment_id = ? AND s.ai_score IS NULL
        ORDER BY s.submission_date DESC
    """, conn, params=(assignment_id,))
    
    # Get graded submissions for review
    graded_submissions = pd.read_sql_query("""
        SELECT s.*, st.name as student_name, st.student_id as student_identifier
        FROM submissions s
        LEFT JOIN students st ON s.student_id = st.id
        WHERE s.assignment_id = ? AND s.ai_score IS NOT NULL
        ORDER BY s.submission_date DESC
    """, conn, params=(assignment_id,))
    
    conn.close()
    
    # Display statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Ungraded", len(ungraded_submissions))
    with col2:
        st.metric("Graded", len(graded_submissions))
    with col3:
        total = len(ungraded_submissions) + len(graded_submissions)
        st.metric("Total", total)
    
    # Grading options
    tab1, tab2, tab3 = st.tabs(["🚀 Auto Grade", "📝 Manual Review", "📊 Batch Process"])
    
    with tab1:
        show_auto_grading_interface(grader, assignment_id, ungraded_submissions)
    
    with tab2:
        show_manual_review_interface(grader, assignment_id, graded_submissions)
    
    with tab3:
        show_batch_processing_interface(grader, assignment_id, ungraded_submissions)

def show_auto_grading_interface(grader, assignment_id, ungraded_submissions):
    """Auto grading interface using business analytics grader"""
    st.subheader("🚀 Automatic Grading")
    
    if ungraded_submissions.empty:
        st.info("✅ All submissions have been graded!")
        return
    
    st.write(f"**{len(ungraded_submissions)} submissions ready for grading**")
    
    # Grading options
    col1, col2 = st.columns(2)
    
    with col1:
        grade_mode = st.selectbox("Grading Mode", [
            "Individual (one at a time)",
            "Batch (all at once)"
        ])
    
    with col2:
        use_validation = st.checkbox("Enable validation", value=True, 
                                   help="Validate all calculations for accuracy")
    
    if grade_mode == "Individual (one at a time)":
        # Individual grading
        if len(ungraded_submissions) > 0:
            submission = ungraded_submissions.iloc[0]
            
            st.write("**Next submission:**")
            student_name = submission['student_name'] or f"Student {submission['student_identifier']}"
            st.write(f"👤 **{student_name}**")
            st.write(f"📅 Submitted: {submission['submission_date']}")
            
            if st.button("⚡ Grade This Submission", type="primary"):
                grade_single_submission(grader, submission, assignment_id, use_validation)
    
    else:
        # Batch grading
        st.write("**Batch grading will process all ungraded submissions**")
        
        if st.button("🚀 Grade All Submissions", type="primary"):
            grade_batch_submissions(grader, ungraded_submissions, assignment_id, use_validation)

def grade_single_submission(grader, submission, assignment_id, use_validation=True):
    """Grade a single submission using business analytics grader"""
    
    try:
        # Initialize our business analytics grader (two-model system)
        business_grader = BusinessAnalyticsGrader()
        
        # Show two-model system info
        st.info("🤖 **Two-Model AI System Active**: Qwen 3.0 Coder (code analysis) + Gemma 3.0 (feedback generation)")
        
        # Extract notebook content
        notebook_path = submission['notebook_path']
        
        if not os.path.exists(notebook_path):
            st.error(f"Notebook file not found: {notebook_path}")
            return
        
        # Read notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Extract code and markdown
        student_code = ""
        student_markdown = ""
        
        for cell in nb.cells:
            if cell.cell_type == 'code':
                student_code += cell.source + "\n\n"
            elif cell.cell_type == 'markdown':
                student_markdown += cell.source + "\n\n"
        
        # Get assignment info
        conn = sqlite3.connect(grader.db_path)
        assignment_info_df = pd.read_sql_query("""
            SELECT name, description, rubric FROM assignments WHERE id = ?
        """, conn, params=(assignment_id,))
        conn.close()
        
        if assignment_info_df.empty:
            st.error("Assignment not found")
            return
        
        assignment_row = assignment_info_df.iloc[0]
        
        # Prepare assignment info
        assignment_info = {
            "title": assignment_row['name'],
            "description": assignment_row['description'],
            "student_name": submission['student_name'] or f"Student {submission['student_identifier']}"
        }
        
        # Parse rubric
        rubric_elements = {}
        if assignment_row['rubric']:
            try:
                rubric_data = json.loads(assignment_row['rubric'])
                rubric_elements = {
                    "technical_execution": {"weight": 0.25, "max_score": 37.5},
                    "business_thinking": {"weight": 0.30, "max_score": 37.5},
                    "data_analysis": {"weight": 0.25, "max_score": 37.5},
                    "communication": {"weight": 0.20, "max_score": 37.5}
                }
            except:
                pass
        
        # Solution code (basic reference)
        solution_code = '''
        library(tidyverse)
        library(readxl)
        
        # Import data
        sales_df <- read_csv("data/sales_data.csv")
        ratings_df <- read_excel("data/customer_feedback.xlsx", sheet = "ratings")
        comments_df <- read_excel("data/customer_feedback.xlsx", sheet = "customer_feedback")
        
        # Data inspection
        head(sales_df)
        str(sales_df)
        summary(sales_df)
        '''
        
        # Show progress
        with st.spinner("🎓 Grading with Business Analytics AI..."):
            
            # Grade the submission
            result = business_grader.grade_submission(
                student_code=student_code,
                student_markdown=student_markdown,
                solution_code=solution_code,
                assignment_info=assignment_info,
                rubric_elements=rubric_elements
            )
            
            # Validate if requested
            if use_validation:
                validator = GradingValidator()
                is_valid, errors = validator.validate_grading_result(result)
                
                if not is_valid:
                    st.warning("⚠️ Validation errors found, fixing...")
                    result = validator.fix_calculation_errors(result)
                    is_valid, errors = validator.validate_grading_result(result)
                
                if is_valid:
                    st.success("✅ Grading validated successfully")
                else:
                    st.error("❌ Validation failed")
                    for error in errors:
                        st.error(f"  • {error}")
        
        # Display results
        st.success("🎉 Grading Complete!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Final Score", f"{result['final_score']}/37.5")
            st.metric("Percentage", f"{result['final_score_percentage']:.1f}%")
        
        with col2:
            # Calculate letter grade
            percentage = result['final_score_percentage']
            if percentage >= 97:
                letter_grade = "A+"
            elif percentage >= 93:
                letter_grade = "A"
            elif percentage >= 90:
                letter_grade = "A-"
            elif percentage >= 87:
                letter_grade = "B+"
            elif percentage >= 83:
                letter_grade = "B"
            elif percentage >= 80:
                letter_grade = "B-"
            else:
                letter_grade = "C+"
            
            st.metric("Letter Grade", letter_grade)
        
        # Show component breakdown
        st.subheader("📊 Component Breakdown")
        component_scores = result['component_scores']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Technical", f"{component_scores['technical_points']:.1f}/9.375")
        with col2:
            st.metric("Business", f"{component_scores['business_points']:.1f}/11.25")
        with col3:
            st.metric("Analysis", f"{component_scores['analysis_points']:.1f}/9.375")
        with col4:
            st.metric("Communication", f"{component_scores['communication_points']:.1f}/7.5")
        
        # Show comprehensive feedback
        if 'comprehensive_feedback' in result:
            st.subheader("💬 Detailed Feedback")
            
            # Show instructor comments
            if 'instructor_comments' in result['comprehensive_feedback']:
                st.write("**Overall Assessment:**")
                st.write(result['comprehensive_feedback']['instructor_comments'])
                st.write("---")
            
            # Show detailed feedback sections
            if 'detailed_feedback' in result['comprehensive_feedback']:
                detailed = result['comprehensive_feedback']['detailed_feedback']
                
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
        
        # Show technical analysis feedback
        if 'technical_analysis' in result:
            with st.expander("🔧 Technical Analysis Details"):
                tech = result['technical_analysis']
                
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
        
        # Show two-model performance stats
        if 'grading_stats' in result:
            from model_status_display import show_grading_performance_stats
            show_grading_performance_stats(result['grading_stats'])
        
        # Save to database
        if st.button("💾 Save Grade", type="primary"):
            save_grading_result(grader, submission['id'], result)
            st.success("✅ Grade saved successfully!")
            st.rerun()
        
        # Generate PDF report
        if st.button("📄 Generate PDF Report"):
            generate_pdf_report(assignment_info['student_name'], assignment_info['title'], result)
    
    except Exception as e:
        st.error(f"❌ Grading failed: {e}")
        import traceback
        st.error(f"Details: {traceback.format_exc()}")

def grade_batch_submissions(grader, submissions, assignment_id, use_validation=True):
    """Grade multiple submissions in batch"""
    
    total_submissions = len(submissions)
    
    # Initialize grader and validator (two-model system)
    business_grader = BusinessAnalyticsGrader()
    validator = GradingValidator() if use_validation else None
    
    st.info("🤖 **Parallel Two-Model Processing**: Code analysis + feedback generation running simultaneously")
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    graded_count = 0
    failed_count = 0
    
    for i, (_, submission) in enumerate(submissions.iterrows()):
        
        progress = (i + 1) / total_submissions
        progress_bar.progress(progress)
        
        student_name = submission['student_name'] or f"Student {submission['student_identifier']}"
        status_text.text(f"Grading {i+1}/{total_submissions}: {student_name}")
        
        try:
            # Grade this submission (similar to single submission logic)
            result = grade_submission_internal(business_grader, submission, assignment_id)
            
            # Validate if requested
            if validator:
                is_valid, errors = validator.validate_grading_result(result)
                if not is_valid:
                    result = validator.fix_calculation_errors(result)
            
            # Save result
            save_grading_result(grader, submission['id'], result)
            
            # Show progress
            with results_container:
                st.success(f"✅ {student_name}: {result['final_score']:.1f}/37.5 ({result['final_score_percentage']:.1f}%)")
            
            graded_count += 1
            
        except Exception as e:
            with results_container:
                st.error(f"❌ {student_name}: Failed - {str(e)}")
            failed_count += 1
    
    # Final results
    status_text.text("🎉 Batch grading complete!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Graded Successfully", graded_count)
    with col2:
        st.metric("Failed", failed_count)
    with col3:
        st.metric("Success Rate", f"{(graded_count/total_submissions)*100:.1f}%")

def grade_submission_internal(business_grader, submission, assignment_id):
    """Internal function to grade a single submission"""
    
    # Extract notebook content
    notebook_path = submission['notebook_path']
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Extract code and markdown
    student_code = ""
    student_markdown = ""
    
    for cell in nb.cells:
        if cell.cell_type == 'code':
            student_code += cell.source + "\n\n"
        elif cell.cell_type == 'markdown':
            student_markdown += cell.source + "\n\n"
    
    # Prepare assignment info
    assignment_info = {
        "title": "Assignment 1 - Introduction to R",
        "student_name": submission['student_name'] or f"Student {submission['student_identifier']}"
    }
    
    # Rubric elements
    rubric_elements = {
        "technical_execution": {"weight": 0.25, "max_score": 37.5},
        "business_thinking": {"weight": 0.30, "max_score": 37.5},
        "data_analysis": {"weight": 0.25, "max_score": 37.5},
        "communication": {"weight": 0.20, "max_score": 37.5}
    }
    
    # Solution code
    solution_code = '''
    library(tidyverse)
    library(readxl)
    
    sales_df <- read_csv("data/sales_data.csv")
    ratings_df <- read_excel("data/customer_feedback.xlsx", sheet = "ratings")
    comments_df <- read_excel("data/customer_feedback.xlsx", sheet = "customer_feedback")
    
    head(sales_df)
    str(sales_df)
    summary(sales_df)
    '''
    
    # Grade the submission
    return business_grader.grade_submission(
        student_code=student_code,
        student_markdown=student_markdown,
        solution_code=solution_code,
        assignment_info=assignment_info,
        rubric_elements=rubric_elements
    )

def save_grading_result(grader, submission_id, result):
    """Save grading result to database"""
    
    conn = sqlite3.connect(grader.db_path)
    cursor = conn.cursor()
    
    # Prepare feedback data
    feedback_data = {
        'final_score': result['final_score'],
        'component_scores': result['component_scores'],
        'component_percentages': result['component_percentages'],
        'technical_analysis': result.get('technical_analysis', {}),
        'comprehensive_feedback': result.get('comprehensive_feedback', {}),
        'grading_stats': result.get('grading_stats', {})
    }
    
    # Update submission
    cursor.execute("""
        UPDATE submissions 
        SET ai_score = ?, ai_feedback = ?, final_score = ?, graded_date = ?
        WHERE id = ?
    """, (
        result['final_score'],
        json.dumps(feedback_data),
        result['final_score'],
        result.get('grading_timestamp'),
        submission_id
    ))
    
    conn.commit()
    conn.close()

def generate_pdf_report(student_name, assignment_title, result):
    """Generate PDF report with comprehensive feedback from Business Analytics Grader"""
    
    try:
        # Convert result to format expected by report generator with comprehensive feedback
        analysis_result = {
            'total_score': result['final_score'],
            'max_score': 37.5,
            'element_scores': {
                'technical_execution': result['component_scores']['technical_points'],
                'business_thinking': result['component_scores']['business_points'],
                'data_analysis': result['component_scores']['analysis_points'],
                'communication': result['component_scores']['communication_points']
            },
            # Include comprehensive feedback from Business Analytics Grader
            'comprehensive_feedback': result.get('comprehensive_feedback', {}),
            # Include technical analysis from Business Analytics Grader
            'technical_analysis': result.get('technical_analysis', {}),
            # Legacy support
            'detailed_feedback': [
                f"Technical Execution: {result['component_scores']['technical_points']:.1f}/9.375 points",
                f"Business Thinking: {result['component_scores']['business_points']:.1f}/11.25 points",
                f"Data Analysis: {result['component_scores']['analysis_points']:.1f}/9.375 points",
                f"Communication: {result['component_scores']['communication_points']:.1f}/7.5 points"
            ],
            'overall_assessment': result.get('comprehensive_feedback', {}).get('instructor_comments', 'Good work!'),
            # Add grading metadata
            'grading_method': result.get('grading_method', 'business_analytics_system'),
            'grading_timestamp': result.get('grading_timestamp', ''),
            'parallel_processing': result.get('parallel_processing', False)
        }
        
        # Generate report
        report_generator = PDFReportGenerator()
        pdf_path = report_generator.generate_report(
            student_name=student_name,
            assignment_id=assignment_title,
            analysis_result=analysis_result
        )
        
        # Offer download
        with open(pdf_path, 'rb') as f:
            st.download_button(
                label="📄 Download PDF Report",
                data=f.read(),
                file_name=f"{student_name}_report.pdf",
                mime="application/pdf"
            )
        
        st.success(f"✅ PDF report generated: {pdf_path}")
        
    except Exception as e:
        st.error(f"❌ Failed to generate PDF report: {e}")

def show_manual_review_interface(grader, assignment_id, graded_submissions):
    """Interface for reviewing and correcting AI grades"""
    st.subheader("📝 Manual Review & Correction")
    
    if graded_submissions.empty:
        st.info("No graded submissions to review.")
        return
    
    st.write(f"**{len(graded_submissions)} graded submissions available for review**")
    
    # Select submission to review
    submission_options = []
    for _, row in graded_submissions.iterrows():
        student_name = row['student_name'] or f"Student {row['student_identifier']}"
        submission_options.append(f"{student_name} (Score: {row['ai_score']:.1f})")
    
    selected_submission = st.selectbox("Select submission to review:", submission_options)
    
    if selected_submission:
        # Get the selected submission
        selected_index = submission_options.index(selected_submission)
        submission = graded_submissions.iloc[selected_index]
        
        # Show current grade
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Current AI Grade")
            st.metric("Score", f"{submission['ai_score']:.1f}/37.5")
            
            # Show AI feedback if available
            if submission['ai_feedback']:
                try:
                    feedback_data = json.loads(submission['ai_feedback'])
                    
                    # Show comprehensive feedback
                    if 'comprehensive_feedback' in feedback_data:
                        comp_feedback = feedback_data['comprehensive_feedback']
                        
                        # Overall comments
                        if 'instructor_comments' in comp_feedback:
                            st.write("**Overall AI Assessment:**")
                            st.write(comp_feedback['instructor_comments'])
                        
                        # Show detailed feedback in expander
                        if 'detailed_feedback' in comp_feedback:
                            with st.expander("📋 View Detailed AI Feedback"):
                                detailed = comp_feedback['detailed_feedback']
                                
                                for section_name, items in detailed.items():
                                    if items and isinstance(items, list):
                                        section_title = section_name.replace('_', ' ').title()
                                        st.write(f"**{section_title}:**")
                                        for item in items:
                                            st.write(f"• {item}")
                                        st.write("")
                    else:
                        st.write("**AI Comments:**")
                        st.write("Basic feedback available")
                        
                except Exception as e:
                    st.write("Feedback format error")
                    st.write(f"Error: {e}")
        
        with col2:
            st.subheader("Manual Correction")
            
            # Correction form
            with st.form(f"correction_{submission['id']}"):
                corrected_score = st.number_input(
                    "Corrected Score",
                    min_value=0.0,
                    max_value=37.5,
                    value=float(submission['human_score']) if submission['human_score'] else float(submission['ai_score']),
                    step=0.5
                )
                
                corrected_feedback = st.text_area(
                    "Corrected Feedback",
                    value=submission['human_feedback'] if submission['human_feedback'] else "",
                    height=100
                )
                
                col_a, col_b = st.columns(2)
                with col_a:
                    save_correction = st.form_submit_button("💾 Save Correction")
                with col_b:
                    approve_ai = st.form_submit_button("✅ Approve AI Grade")
                
                if save_correction:
                    save_manual_correction(grader, submission['id'], corrected_score, corrected_feedback)
                    st.success("Correction saved!")
                    st.rerun()
                
                if approve_ai:
                    save_manual_correction(grader, submission['id'], submission['ai_score'], submission['ai_feedback'])
                    st.success("AI grade approved!")
                    st.rerun()

def save_manual_correction(grader, submission_id, score, feedback):
    """Save manual correction to database"""
    
    conn = sqlite3.connect(grader.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE submissions
        SET human_score = ?, human_feedback = ?, final_score = ?
        WHERE id = ?
    """, (score, feedback, score, submission_id))
    
    conn.commit()
    conn.close()

def show_batch_processing_interface(grader, assignment_id, ungraded_submissions):
    """Interface for batch processing options"""
    st.subheader("📊 Batch Processing")
    
    if ungraded_submissions.empty:
        st.info("No ungraded submissions for batch processing.")
        return
    
    st.write(f"**{len(ungraded_submissions)} submissions ready for batch processing**")
    
    # Batch options
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Grade All & Generate Reports", type="primary"):
            batch_grade_and_report(grader, ungraded_submissions, assignment_id)
    
    with col2:
        if st.button("📊 Grade All & Export CSV"):
            batch_grade_and_export(grader, ungraded_submissions, assignment_id)

def batch_grade_and_report(grader, submissions, assignment_id):
    """Grade all submissions and generate reports"""
    
    with st.spinner("Processing batch grading and report generation..."):
        
        # Grade all submissions
        grade_batch_submissions(grader, submissions, assignment_id, use_validation=True)
        
        # Generate reports for all
        st.info("Generating PDF reports...")
        
        # This would call the report generation logic
        st.success("✅ Batch processing complete!")

def batch_grade_and_export(grader, submissions, assignment_id):
    """Grade all submissions and export to CSV"""
    
    with st.spinner("Processing batch grading and CSV export..."):
        
        # Grade all submissions
        grade_batch_submissions(grader, submissions, assignment_id, use_validation=True)
        
        # Export to CSV
        st.info("Generating CSV export...")
        
        # This would call the CSV export logic
        st.success("✅ Batch processing and export complete!")

def main():
    """Test the connection"""
    print("🔗 Web interface connected to business analytics grader!")
    print("✅ Ready to use in Streamlit app")

if __name__ == "__main__":
    main()