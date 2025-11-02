"""
Enhanced Training Database Setup
Initializes and manages the enhanced training database
"""
import sqlite3
import os

def setup_enhanced_training_database():
    """Set up the enhanced training database with required tables"""
    db_path = "enhanced_training.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Assignments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            total_points INTEGER DEFAULT 37.5,
            rubric TEXT,
            template_notebook TEXT,
            solution_notebook TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    # Training data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_training_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER,
            submission_id INTEGER,
            cell_content TEXT,
            expected_output TEXT,
            human_score REAL,
            ai_score REAL,
            ai_feedback TEXT,
            human_feedback TEXT,
            features TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            corrected_at TIMESTAMP,
            FOREIGN KEY (assignment_id) REFERENCES assignments (id),
            FOREIGN KEY (submission_id) REFERENCES submissions (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    return db_path
