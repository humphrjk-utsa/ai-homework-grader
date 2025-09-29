#!/usr/bin/env python3
"""
Force the web interface to use BusinessAnalyticsGrader by replacing the grading function
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import os
import nbformat
from business_analytics_grader import BusinessAnalyticsGrader
from grading_validator import GradingValidator

def force_business_analytics_grading():
    """Force use of BusinessAnalyticsGrader for web interface"""
    
    st.title("🤖 Force Business Analytics Grading Test")
    
    # Check database
    db_path = "grading_database.db"
    
    if not os.path.exists(db_path):
        st.error("Database not found. Run fix_web_interface.py first.")
        return
    
    conn = sqlite3.connect(db_path)
    
    # Get ungraded submissions
    ungraded = pd.read_sql_query("""
        SELECT s.*, st.name as student_name, st.student_id as student_identifier
        FROM submissions s
        LEFT JOIN students st ON s.student_id = st.id
        WHERE s.ai_score IS NULL
        LIMIT 5
    """, conn)
    
    conn.close()
    
    if ungraded.empty:
        st.info("No ungraded submissions found.")
        return
    
    st.write(f"Found {len(ungraded)} ungraded submissions")
    
    # Select a submission to grade
    submission_options = []
    for _, row in ungraded.iterrows():
        student_name = row['student_name'] or f"Student {row['student_identifier']}"
        submission_options.append(f"{student_name}")
    
    selected_student = st.selectbox("Select student to grade:", submission_options)
    
    if st.button("🚀 Grade with BusinessAnalyticsGrader", type="primary"):
        
        # Get the selected submission
        selected_index = submission_options.index(selected_student)
        submission = ungraded.iloc[selected_index]
        
        st.info("🤖 **FORCING BusinessAnalyticsGrader Usage**")
        
        try:
            # Force initialization of BusinessAnalyticsGrader
            st.write("Initializing BusinessAnalyticsGrader...")
            business_grader = BusinessAnalyticsGrader()
            
            # Extract notebook content
            notebook_path = submission['notebook_path']
            
            if not os.path.exists(notebook_path):
                st.error(f"Notebook not found: {notebook_path}")
                return
            
            st.write("Reading notebook...")
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
            
            # Extract content
            student_code = ""
            student_markdown = ""
            
            for cell in nb.cells:
                if cell.cell_type == 'code':
                    student_code += cell.source + "\n\n"
                elif cell.cell_type == 'markdown':
                    student_markdown += cell.source + "\n\n"
            
            st.write(f"Extracted {len(student_code)} chars of code, {len(student_markdown)} chars of markdown")
            
            # Prepare grading parameters
            assignment_info = {
                "title": "Assignment 1 - Introduction to R",
                "student_name": submission['student_name'] or f"Student {submission['student_identifier']}"
            }
            
            rubric_elements = {
                "technical_execution": {"weight": 0.25, "max_score": 37.5},
                "business_thinking": {"weight": 0.30, "max_score": 37.5},
                "data_analysis": {"weight": 0.25, "max_score": 37.5},
                "communication": {"weight": 0.20, "max_score": 37.5}
            }
            
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
            
            # Grade with BusinessAnalyticsGrader
            st.write("🚀 Grading with BusinessAnalyticsGrader...")
            
            with st.spinner("Grading in progress..."):
                result = business_grader.grade_submission(
                    student_code=student_code,
                    student_markdown=student_markdown,
                    solution_code=solution_code,
                    assignment_info=assignment_info,
                    rubric_elements=rubric_elements
                )
            
            # Display results
            if result:
                st.success("🎉 BusinessAnalyticsGrader Success!")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Final Score", f"{result['final_score']}/37.5")
                
                with col2:
                    st.metric("Percentage", f"{result['final_score_percentage']:.1f}%")
                
                with col3:
                    st.metric("Method", result.get('grading_method', 'Unknown'))
                
                # Show component breakdown
                st.subheader("📊 Component Scores")
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
                
                # Show performance stats
                if 'grading_stats' in result:
                    st.subheader("⚡ Two-Model Performance")
                    stats = result['grading_stats']
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Code Analysis", f"{stats.get('code_analysis_time', 0):.1f}s")
                    with col2:
                        st.metric("Feedback Generation", f"{stats.get('feedback_generation_time', 0):.1f}s")
                    with col3:
                        st.metric("Parallel Speedup", f"{stats.get('parallel_efficiency', 0):.1f}x")
                
                # Show feedback
                if 'comprehensive_feedback' in result:
                    st.subheader("💬 Instructor Comments")
                    feedback = result['comprehensive_feedback']
                    if 'instructor_comments' in feedback:
                        st.write(feedback['instructor_comments'])
                
                # Validate result
                validator = GradingValidator()
                is_valid, errors = validator.validate_grading_result(result)
                
                if is_valid:
                    st.success("✅ Grading result validated successfully")
                else:
                    st.warning("⚠️ Validation errors found:")
                    for error in errors:
                        st.error(f"  • {error}")
                
                # Save to database
                if st.button("💾 Save This Grade"):
                    try:
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        
                        feedback_data = {
                            'final_score': result['final_score'],
                            'component_scores': result['component_scores'],
                            'comprehensive_feedback': result.get('comprehensive_feedback', {}),
                            'grading_method': 'business_analytics_system'
                        }
                        
                        cursor.execute("""
                            UPDATE submissions 
                            SET ai_score = ?, ai_feedback = ?, final_score = ?, graded_date = ?
                            WHERE id = ?
                        """, (
                            result['final_score'],
                            json.dumps(feedback_data),
                            result['final_score'],
                            result.get('grading_timestamp'),
                            submission['id']
                        ))
                        
                        conn.commit()
                        conn.close()
                        
                        st.success("✅ Grade saved to database!")
                        
                    except Exception as e:
                        st.error(f"❌ Failed to save grade: {e}")
            
            else:
                st.error("❌ BusinessAnalyticsGrader returned no result")
        
        except Exception as e:
            st.error(f"❌ BusinessAnalyticsGrader failed: {e}")
            import traceback
            st.error(f"Details: {traceback.format_exc()}")

if __name__ == "__main__":
    force_business_analytics_grading()