#!/usr/bin/env python3
"""
Debug the grading issue by tracing exactly what happens during grading
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import os
import nbformat
from business_analytics_grader import BusinessAnalyticsGrader
from grading_validator import GradingValidator

def debug_grade_submissions_page(grader):
    """Debug version of grade submissions page"""
    st.header("🔍 DEBUG: Grade Submissions")
    
    st.info("🐛 **DEBUG MODE**: This will show exactly what grading system is being used")
    
    # Check database connection
    try:
        conn = sqlite3.connect(grader.db_path)
        assignments = pd.read_sql_query("SELECT id, name FROM assignments ORDER BY created_date DESC", conn)
        
        if assignments.empty:
            st.warning("No assignments found.")
            conn.close()
            return
        
        st.success(f"✅ Database connected: {len(assignments)} assignments found")
        
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
        
        conn.close()
        
        st.write(f"📊 Found {len(ungraded_submissions)} ungraded submissions")
        
        if ungraded_submissions.empty:
            st.info("✅ All submissions have been graded!")
            return
        
        # Show first submission for testing
        submission = ungraded_submissions.iloc[0]
        student_name = submission['student_name'] or f"Student {submission['student_identifier']}"
        
        st.write(f"**Testing with:** {student_name}")
        st.write(f"**Notebook path:** {submission['notebook_path']}")
        
        if st.button("🔍 DEBUG: Test BusinessAnalyticsGrader", type="primary"):
            
            st.write("---")
            st.subheader("🐛 DEBUG TRACE")
            
            # Step 1: Test BusinessAnalyticsGrader initialization
            st.write("**Step 1:** Initializing BusinessAnalyticsGrader...")
            try:
                business_grader = BusinessAnalyticsGrader()
                st.success("✅ BusinessAnalyticsGrader initialized")
            except Exception as e:
                st.error(f"❌ BusinessAnalyticsGrader initialization failed: {e}")
                return
            
            # Step 2: Test Ollama connection
            st.write("**Step 2:** Testing Ollama connection...")
            try:
                if business_grader.check_ollama_connection():
                    st.success("✅ Ollama connection OK")
                else:
                    st.error("❌ Ollama connection failed")
                    return
            except Exception as e:
                st.error(f"❌ Ollama connection error: {e}")
                return
            
            # Step 3: Test model availability
            st.write("**Step 3:** Testing model availability...")
            try:
                if business_grader.check_models_available():
                    st.success("✅ Required models available")
                else:
                    st.error("❌ Required models not available")
                    return
            except Exception as e:
                st.error(f"❌ Model availability error: {e}")
                return
            
            # Step 4: Test notebook reading
            st.write("**Step 4:** Reading notebook...")
            try:
                notebook_path = submission['notebook_path']
                
                if not os.path.exists(notebook_path):
                    st.error(f"❌ Notebook file not found: {notebook_path}")
                    return
                
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
                
                st.success(f"✅ Notebook read: {len(student_code)} chars code, {len(student_markdown)} chars markdown")
                
            except Exception as e:
                st.error(f"❌ Notebook reading failed: {e}")
                return
            
            # Step 5: Test grading
            st.write("**Step 5:** Testing grading...")
            try:
                assignment_info = {
                    "title": selected_assignment,
                    "student_name": student_name
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
                '''
                
                st.write("🚀 Calling business_grader.grade_submission()...")
                
                with st.spinner("Grading in progress..."):
                    result = business_grader.grade_submission(
                        student_code=student_code,
                        student_markdown=student_markdown,
                        solution_code=solution_code,
                        assignment_info=assignment_info,
                        rubric_elements=rubric_elements
                    )
                
                if result:
                    st.success("✅ BusinessAnalyticsGrader SUCCESS!")
                    
                    # Show detailed results
                    st.write("**RESULT DETAILS:**")
                    st.write(f"- Final Score: {result['final_score']}/37.5 ({result['final_score_percentage']:.1f}%)")
                    st.write(f"- Grading Method: {result.get('grading_method', 'Unknown')}")
                    
                    if 'grading_stats' in result:
                        stats = result['grading_stats']
                        st.write(f"- Code Analysis Time: {stats.get('code_analysis_time', 0):.1f}s")
                        st.write(f"- Feedback Generation Time: {stats.get('feedback_generation_time', 0):.1f}s")
                        st.write(f"- Parallel Efficiency: {stats.get('parallel_efficiency', 0):.1f}x")
                    
                    # Show component scores
                    if 'component_scores' in result:
                        st.write("**COMPONENT SCORES:**")
                        components = result['component_scores']
                        st.write(f"- Technical: {components.get('technical_points', 0):.1f}/9.375")
                        st.write(f"- Business: {components.get('business_points', 0):.1f}/11.25")
                        st.write(f"- Analysis: {components.get('analysis_points', 0):.1f}/9.375")
                        st.write(f"- Communication: {components.get('communication_points', 0):.1f}/7.5")
                    
                    # Validate
                    validator = GradingValidator()
                    is_valid, errors = validator.validate_grading_result(result)
                    
                    if is_valid:
                        st.success("✅ Validation passed")
                    else:
                        st.warning("⚠️ Validation issues:")
                        for error in errors:
                            st.write(f"  - {error}")
                    
                    st.write("---")
                    st.success("🎉 **BusinessAnalyticsGrader is working correctly!**")
                    st.info("If the web interface is still showing fallback results, there may be a different code path being used.")
                
                else:
                    st.error("❌ BusinessAnalyticsGrader returned no result")
                
            except Exception as e:
                st.error(f"❌ Grading failed: {e}")
                import traceback
                st.error(f"Full traceback: {traceback.format_exc()}")
    
    except Exception as e:
        st.error(f"❌ Debug failed: {e}")
        import traceback
        st.error(f"Full traceback: {traceback.format_exc()}")

# Replace the grade_submissions_page function
grade_submissions_page = debug_grade_submissions_page