import streamlit as st
import pandas as pd
import json
import os
import sqlite3
from datetime import datetime
import nbformat
from nbconvert import HTMLExporter
import subprocess
import tempfile
import shutil
from pathlib import Path
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Import our modules
from assignment_manager import create_assignment_page, upload_submissions_page
from assignment_editor import assignment_management_page, get_assignment_rubric
from training_interface import TrainingInterface
from connect_web_interface import grade_submissions_page
from grading_interface import view_results_page
from model_status_display import show_two_model_status

# Configure page
st.set_page_config(
    page_title="Homework Grader",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'current_assignment' not in st.session_state:
    st.session_state.current_assignment = None
if 'current_student' not in st.session_state:
    st.session_state.current_student = None
if 'grading_data' not in st.session_state:
    st.session_state.grading_data = {}
if 'page' not in st.session_state:
    st.session_state.page = None

class HomeworkGrader:
    def __init__(self):
        # Use relative paths when running from homework_grader directory
        self.db_path = "grading_database.db"
        self.assignments_dir = "assignments"
        self.submissions_dir = "submissions"
        self.models_dir = "models"
        
        # Create directories
        for dir_path in [self.assignments_dir, self.submissions_dir, self.models_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for storing grading data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Assignments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                total_points INTEGER,
                rubric TEXT,
                template_notebook TEXT,
                solution_notebook TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT,
                email TEXT
            )
        ''')
        
        # Submissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assignment_id INTEGER,
                student_id TEXT,
                notebook_path TEXT,
                submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ai_score REAL,
                ai_feedback TEXT,
                human_score REAL,
                human_feedback TEXT,
                final_score REAL,
                graded_date TIMESTAMP,
                FOREIGN KEY (assignment_id) REFERENCES assignments (id)
            )
        ''')
        
        # AI training data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assignment_id INTEGER,
                cell_content TEXT,
                expected_output TEXT,
                human_score REAL,
                ai_score REAL,
                ai_feedback TEXT,
                human_feedback TEXT,
                features TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                corrected_at TIMESTAMP,
                FOREIGN KEY (assignment_id) REFERENCES assignments (id)
            )
        ''')
        
        # Add ai_score column if it doesn't exist (for existing databases)
        try:
            cursor.execute('ALTER TABLE ai_training_data ADD COLUMN ai_score REAL')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Add ai_feedback column if it doesn't exist
        try:
            cursor.execute('ALTER TABLE ai_training_data ADD COLUMN ai_feedback TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Add corrected_at column if it doesn't exist
        try:
            cursor.execute('ALTER TABLE ai_training_data ADD COLUMN corrected_at TIMESTAMP')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        conn.commit()
        conn.close()

def main():
    st.title("📚 AI-Powered Homework Grader")
    st.markdown("---")
    
    grader = HomeworkGrader()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Dashboard", "Assignment Management", "Upload Submissions", "Grade Submissions", "View Results", "AI Training"]
    )
    
    # Show two-model system status in sidebar
    try:
        from model_status_display import show_two_model_status
        show_two_model_status()
    except Exception as e:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🤖 Two-Model AI System")
        st.sidebar.error(f"Status check failed: {str(e)[:30]}...")
        st.sidebar.info("💡 Qwen 3.0 Coder + Gemma 3.0 system will load when needed")
    
    if page == "Dashboard":
        show_dashboard(grader)
    elif page == "Assignment Management":
        assignment_management_page(grader)
    elif page == "Upload Submissions":
        upload_submissions_page(grader)
    elif page == "Grade Submissions":
        grade_submissions_page(grader)
    elif page == "View Results":
        view_results_page(grader)
    elif page == "AI Training":
        training_interface = TrainingInterface(grader)
        training_interface.show_training_dashboard()

def show_dashboard(grader):
    st.header("📊 Dashboard")
    
    conn = sqlite3.connect(grader.db_path)
    
    # Get statistics
    assignments_count = pd.read_sql_query("SELECT COUNT(*) as count FROM assignments", conn).iloc[0]['count']
    submissions_count = pd.read_sql_query("SELECT COUNT(*) as count FROM submissions", conn).iloc[0]['count']
    graded_count = pd.read_sql_query("SELECT COUNT(*) as count FROM submissions WHERE final_score IS NOT NULL", conn).iloc[0]['count']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Assignments", assignments_count)
    
    with col2:
        st.metric("Total Submissions", submissions_count)
    
    with col3:
        st.metric("Graded Submissions", graded_count)
    
    # Recent activity
    st.subheader("Recent Activity")
    recent_submissions = pd.read_sql_query("""
        SELECT s.student_id, a.name as assignment_name, s.submission_date, s.final_score
        FROM submissions s
        JOIN assignments a ON s.assignment_id = a.id
        ORDER BY s.submission_date DESC
        LIMIT 10
    """, conn)
    
    if not recent_submissions.empty:
        st.dataframe(recent_submissions)
    else:
        st.info("No submissions yet.")
    
    conn.close()

if __name__ == "__main__":
    main()