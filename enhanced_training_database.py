#!/usr/bin/env python3
"""
Enhanced Training Database Setup
Creates and manages database schema for the enhanced AI training interface
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, Dict, Any

class EnhancedTrainingDatabase:
    """Database management for enhanced training interface"""
    
    def __init__(self, db_path: str = "grading_database.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Set up database tables and indexes for enhanced training"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create human_feedback table for instructor corrections
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS human_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id INTEGER UNIQUE NOT NULL,
                human_score REAL NOT NULL CHECK (human_score >= 0 AND human_score <= 37.5),
                human_feedback TEXT,
                instructor_id TEXT DEFAULT 'instructor',
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (submission_id) REFERENCES submissions (id) ON DELETE CASCADE
            )
        """)
        
        # Create training_stats table for analytics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assignment_id INTEGER NOT NULL,
                calculation_date DATE DEFAULT (date('now')),
                total_submissions INTEGER DEFAULT 0,
                ai_only_submissions INTEGER DEFAULT 0,
                human_reviewed_submissions INTEGER DEFAULT 0,
                avg_ai_score REAL DEFAULT 0.0,
                avg_human_score REAL DEFAULT 0.0,
                avg_score_adjustment REAL DEFAULT 0.0,
                score_boost_count INTEGER DEFAULT 0,
                score_reduction_count INTEGER DEFAULT 0,
                ai_accuracy_percentage REAL DEFAULT 0.0,
                FOREIGN KEY (assignment_id) REFERENCES assignments (id)
            )
        """)
        
        # Create training_sessions table for tracking review sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assignment_id INTEGER NOT NULL,
                instructor_id TEXT DEFAULT 'instructor',
                session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_end TIMESTAMP,
                submissions_reviewed INTEGER DEFAULT 0,
                total_score_adjustments REAL DEFAULT 0.0,
                session_notes TEXT,
                FOREIGN KEY (assignment_id) REFERENCES assignments (id)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_human_feedback_submission ON human_feedback (submission_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_human_feedback_updated ON human_feedback (last_updated)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_training_stats_assignment ON training_stats (assignment_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_training_stats_date ON training_stats (calculation_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_training_sessions_assignment ON training_sessions (assignment_id)")
        
        # Create trigger to update last_updated timestamp
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_human_feedback_timestamp 
            AFTER UPDATE ON human_feedback
            BEGIN
                UPDATE human_feedback 
                SET last_updated = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END
        """)
        
        # Create view for comprehensive training reports - SINGLE SOURCE OF TRUTH
        # Note: Using submissions table directly (no grading_results table)
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS training_report_view AS
            SELECT 
                s.id as submission_id,
                COALESCE(st.name, 'Unknown') as student_name,
                COALESCE(st.student_id, s.student_id) as student_id,
                a.name as assignment_title,
                a.id as assignment_id,
                -- AI Score: From submissions table
                COALESCE(s.ai_score, 0) as ai_score,
                COALESCE((s.ai_score / 37.5 * 100), 0) as ai_percentage,
                -- Human Score: Always from human_feedback table (authoritative for human scores)
                hf.human_score,
                CASE WHEN hf.human_score IS NOT NULL THEN (hf.human_score / 37.5 * 100) ELSE NULL END as human_percentage,
                -- Final Score: Human score if exists, otherwise AI score (single source of truth)
                COALESCE(hf.human_score, s.final_score, s.ai_score, 0) as final_score,
                -- Score adjustment calculation
                CASE WHEN hf.human_score IS NOT NULL THEN (hf.human_score - COALESCE(s.ai_score, 0)) ELSE NULL END as score_adjustment,
                -- Review status based on authoritative sources
                CASE 
                    WHEN hf.human_score IS NULL THEN 'AI Only'
                    WHEN hf.human_score > COALESCE(s.ai_score, 0) THEN 'Boosted'
                    WHEN hf.human_score < COALESCE(s.ai_score, 0) THEN 'Reduced'
                    ELSE 'Confirmed'
                END as review_status,
                -- Grade category based on final score
                CASE 
                    WHEN COALESCE(hf.human_score, s.final_score, s.ai_score, 0) >= 35 THEN 'Excellent'
                    WHEN COALESCE(hf.human_score, s.final_score, s.ai_score, 0) >= 30 THEN 'Good'
                    WHEN COALESCE(hf.human_score, s.final_score, s.ai_score, 0) >= 25 THEN 'Fair'
                    ELSE 'Needs Work'
                END as grade_category,
                s.submission_date,
                hf.last_updated as review_date,
                NULL as grading_method,
                s.ai_feedback,
                hf.human_feedback,
                s.notebook_path
            FROM submissions s
            LEFT JOIN students st ON s.student_id = st.id
            JOIN assignments a ON s.assignment_id = a.id
            LEFT JOIN human_feedback hf ON s.id = hf.submission_id
        """)
        
        conn.commit()
        conn.close()
    
    def migrate_existing_data(self):
        """Migrate existing data to new schema if needed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if we need to migrate data from submissions table
        cursor.execute("PRAGMA table_info(submissions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Migrate human scores from submissions table to human_feedback table
        if 'human_score' in columns:
            cursor.execute("""
                INSERT OR IGNORE INTO human_feedback (submission_id, human_score, human_feedback)
                SELECT id, human_score, human_feedback
                FROM submissions 
                WHERE human_score IS NOT NULL
            """)
        
        # Add missing columns to submissions table if needed
        if 'notebook_path' not in columns:
            cursor.execute("ALTER TABLE submissions ADD COLUMN notebook_path TEXT")
        
        if 'submission_date' not in columns:
            cursor.execute("ALTER TABLE submissions ADD COLUMN submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
        conn.commit()
        conn.close()
    
    def calculate_training_stats(self, assignment_id: Optional[int] = None):
        """Calculate and store training statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get assignments to calculate stats for
        if assignment_id:
            assignments = [(assignment_id,)]
        else:
            cursor.execute("SELECT DISTINCT id FROM assignments")
            assignments = cursor.fetchall()
        
        for (aid,) in assignments:
            # Calculate statistics for this assignment
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_submissions,
                    COUNT(CASE WHEN hf.human_score IS NULL THEN 1 END) as ai_only,
                    COUNT(CASE WHEN hf.human_score IS NOT NULL THEN 1 END) as human_reviewed,
                    AVG(s.ai_score) as avg_ai_score,
                    AVG(hf.human_score) as avg_human_score,
                    AVG(CASE WHEN hf.human_score IS NOT NULL THEN hf.human_score - s.ai_score END) as avg_adjustment,
                    COUNT(CASE WHEN hf.human_score > s.ai_score THEN 1 END) as boost_count,
                    COUNT(CASE WHEN hf.human_score < s.ai_score THEN 1 END) as reduction_count
                FROM submissions s
                LEFT JOIN human_feedback hf ON s.id = hf.submission_id
                WHERE s.assignment_id = ?
            """, (aid,))
            
            stats = cursor.fetchone()
            
            if stats and stats[0] > 0:  # If there are submissions
                # Calculate AI accuracy (percentage of scores within 2 points)
                cursor.execute("""
                    SELECT COUNT(*) * 100.0 / COUNT(hf.human_score)
                    FROM submissions s
                    JOIN human_feedback hf ON s.id = hf.submission_id
                    WHERE s.assignment_id = ? AND ABS(s.ai_score - hf.human_score) <= 2.0
                """, (aid,))
                
                accuracy_result = cursor.fetchone()
                ai_accuracy = accuracy_result[0] if accuracy_result and accuracy_result[0] else 0.0
                
                # Insert or update training stats
                cursor.execute("""
                    INSERT OR REPLACE INTO training_stats (
                        assignment_id, total_submissions, ai_only_submissions, 
                        human_reviewed_submissions, avg_ai_score, avg_human_score,
                        avg_score_adjustment, score_boost_count, score_reduction_count,
                        ai_accuracy_percentage
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (aid, stats[0], stats[1], stats[2], stats[3] or 0, 
                     stats[4] or 0, stats[5] or 0, stats[6] or 0, stats[7] or 0, ai_accuracy))
        
        conn.commit()
        conn.close()
    
    def cleanup_old_stats(self, days_to_keep: int = 30):
        """Clean up old training statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM training_stats 
            WHERE calculation_date < date('now', '-{} days')
        """.format(days_to_keep))
        
        conn.commit()
        conn.close()
    
    def validate_data_consistency(self) -> Dict[str, Any]:
        """
        Validate data consistency across tables and fix any issues
        
        Returns:
            Dict with validation results and any fixes applied
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        validation_results = {
            'issues_found': [],
            'fixes_applied': [],
            'total_submissions': 0,
            'consistent_records': 0
        }
        
        try:
            # Get all submissions for validation
            cursor.execute("""
                SELECT s.id, s.final_score as sub_final_score, s.human_score as sub_human_score,
                       s.ai_score as s_ai_score, hf.human_score as hf_human_score
                FROM submissions s
                LEFT JOIN human_feedback hf ON s.id = hf.submission_id
            """)
            
            submissions = cursor.fetchall()
            validation_results['total_submissions'] = len(submissions)
            
            for submission in submissions:
                submission_id = submission[0]
                sub_final_score = submission[1]
                sub_human_score = submission[2]
                s_ai_score = submission[3]
                hf_human_score = submission[4]
                
                # Determine what the final score should be (single source of truth)
                expected_final_score = hf_human_score if hf_human_score is not None else (s_ai_score or 0)
                
                issues_for_submission = []
                
                # Check if final_score in submissions table matches expected
                if sub_final_score != expected_final_score:
                    issues_for_submission.append(f"Submission {submission_id}: final_score mismatch")
                    
                    # Fix: Update final_score to match authoritative source
                    cursor.execute("""
                        UPDATE submissions SET final_score = ? WHERE id = ?
                    """, (expected_final_score, submission_id))
                    validation_results['fixes_applied'].append(f"Fixed final_score for submission {submission_id}")
                
                # Check if human_score in submissions matches human_feedback table
                if sub_human_score != hf_human_score:
                    issues_for_submission.append(f"Submission {submission_id}: human_score mismatch")
                    
                    # Fix: Update human_score to match authoritative source
                    cursor.execute("""
                        UPDATE submissions SET human_score = ? WHERE id = ?
                    """, (hf_human_score, submission_id))
                    validation_results['fixes_applied'].append(f"Fixed human_score for submission {submission_id}")
                
                if not issues_for_submission:
                    validation_results['consistent_records'] += 1
                else:
                    validation_results['issues_found'].extend(issues_for_submission)
            
            # Check for orphaned records
            cursor.execute("""
                SELECT hf.submission_id 
                FROM human_feedback hf 
                LEFT JOIN submissions s ON hf.submission_id = s.id 
                WHERE s.id IS NULL
            """)
            orphaned_feedback = cursor.fetchall()
            
            if orphaned_feedback:
                validation_results['issues_found'].append(f"Found {len(orphaned_feedback)} orphaned human_feedback records")
                # Clean up orphaned records
                cursor.execute("""
                    DELETE FROM human_feedback 
                    WHERE submission_id NOT IN (SELECT id FROM submissions)
                """)
                validation_results['fixes_applied'].append(f"Cleaned up {len(orphaned_feedback)} orphaned human_feedback records")
            
            conn.commit()
            
        except Exception as e:
            validation_results['issues_found'].append(f"Validation error: {e}")
            conn.rollback()
        
        finally:
            conn.close()
        
        return validation_results
    
    def get_database_info(self):
        """Get information about the database structure"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        info = {}
        
        # Get table counts
        tables = ['submissions', 'human_feedback', 'training_stats', 'training_sessions']
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                info[f"{table}_count"] = cursor.fetchone()[0]
            except:
                info[f"{table}_count"] = 0
        
        # Get recent activity
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM human_feedback 
                WHERE last_updated >= date('now', '-7 days')
            """)
            info['recent_reviews'] = cursor.fetchone()[0]
        except:
            info['recent_reviews'] = 0
        
        conn.close()
        return info

def setup_enhanced_training_database(db_path: str = "grading_database.db"):
    """Convenience function to set up the enhanced training database"""
    db = EnhancedTrainingDatabase(db_path)
    db.migrate_existing_data()
    db.calculate_training_stats()
    return db

if __name__ == "__main__":
    print("Setting up enhanced training database...")
    db = setup_enhanced_training_database()
    info = db.get_database_info()
    
    print("✅ Database setup complete!")
    print(f"📊 Database info:")
    for key, value in info.items():
        print(f"  - {key}: {value}")