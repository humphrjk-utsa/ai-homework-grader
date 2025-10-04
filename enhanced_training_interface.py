#!/usr/bin/env python3
"""
Enhanced AI Training Review Interface
Comprehensive system for reviewing and correcting AI-generated scores
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import os
import tempfile
import zipfile
import nbformat
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedTrainingInterface:
    """Enhanced AI Training interface with comprehensive review capabilities"""
    
    def __init__(self, db_path: str = "grading_database.db"):
        self.db_path = db_path
        self.setup_logging()
        
    def setup_logging(self):
        """Set up logging for the training interface"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create file handler
        log_file = log_dir / f"training_interface_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
    
    def get_database_connection(self) -> sqlite3.Connection:
        """Get database connection with error handling"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            st.error(f"Database connection failed: {e}")
            raise
    
    def get_assignments(self) -> List[Dict[str, Any]]:
        """Get list of assignments for selection"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT a.id, a.name as title, a.description, 
                       COUNT(s.id) as submission_count,
                       AVG(CASE WHEN s.final_score IS NOT NULL THEN s.final_score ELSE 0 END) as avg_score,
                       COUNT(hf.id) as human_reviewed_count
                FROM assignments a
                LEFT JOIN submissions s ON a.id = s.assignment_id
                LEFT JOIN human_feedback hf ON s.id = hf.submission_id
                GROUP BY a.id, a.name, a.description
                ORDER BY a.id DESC
            """)
            
            assignments = []
            for row in cursor.fetchall():
                assignments.append({
                    'id': row['id'],
                    'title': row['title'] or f"Assignment {row['id']}",
                    'description': row['description'] or "No description",
                    'submission_count': row['submission_count'] or 0,
                    'avg_score': round(row['avg_score'] or 0, 1),
                    'human_reviewed_count': row['human_reviewed_count'] or 0
                })
            
            conn.close()
            return assignments
            
        except Exception as e:
            logger.error(f"Error getting assignments: {e}")
            st.error(f"Error loading assignments: {e}")
            return []
    
    def get_submissions(self, assignment_id: int, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Get submissions for a specific assignment with AI and human scores"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()
            
            # Base query using the training_report_view
            query = """
                SELECT * FROM training_report_view
                WHERE assignment_id = ?
            """
            params = [assignment_id]
            
            # Apply filters if provided
            if filters:
                if filters.get('score_range'):
                    min_score, max_score = filters['score_range']
                    query += " AND final_score BETWEEN ? AND ?"
                    params.extend([min_score, max_score])
                
                if filters.get('review_status') and filters['review_status'] != 'All':
                    if filters['review_status'] == 'AI Only':
                        query += " AND review_status = 'AI Only'"
                    elif filters['review_status'] == 'Human Reviewed':
                        query += " AND review_status != 'AI Only'"
                    elif filters['review_status'] == 'Needs Review':
                        query += " AND review_status = 'AI Only' AND final_score < 30"
                
                if filters.get('student_search'):
                    query += " AND student_name LIKE ?"
                    params.append(f"%{filters['student_search']}%")
            
            query += " ORDER BY student_name"
            
            cursor.execute(query, params)
            
            submissions = []
            for row in cursor.fetchall():
                # Calculate additional indicators
                ai_score = row['ai_score'] or 0
                human_score = row['human_score']
                final_score = row['final_score'] or 0
                
                # Score status indicator
                if human_score is not None:
                    if human_score > ai_score:
                        score_status = "📈 Boosted"
                    elif human_score < ai_score:
                        score_status = "📉 Reduced"
                    else:
                        score_status = "✅ Confirmed"
                else:
                    score_status = "🤖 AI Only"
                
                # Grade indicator
                if final_score >= 35:
                    grade_indicator = "🎉 Excellent"
                elif final_score >= 30:
                    grade_indicator = "👍 Good"
                elif final_score >= 25:
                    grade_indicator = "⚠️ Fair"
                else:
                    grade_indicator = "❌ Needs Work"
                
                submissions.append({
                    'id': row['submission_id'],
                    'student_name': row['student_name'],
                    'student_id': row['student_id'],
                    'notebook_path': row['notebook_path'],
                    'submission_date': row['submission_date'],
                    'ai_score': ai_score,
                    'ai_percentage': row['ai_percentage'] or 0,
                    'human_score': human_score,
                    'human_feedback': row['human_feedback'],
                    'review_date': row['review_date'],
                    'grading_method': row['grading_method'],
                    'ai_feedback': row['ai_feedback'],
                    'score_status': score_status,
                    'grade_indicator': grade_indicator,
                    'final_score': final_score,
                    'grade_category': row['grade_category']
                })
            
            conn.close()
            return submissions
            
        except Exception as e:
            logger.error(f"Error getting submissions for assignment {assignment_id}: {e}")
            st.error(f"Error loading submissions: {e}")
            return []
    
    def get_human_feedback(self, submission_id: int) -> Optional[Dict[str, Any]]:
        """Get existing human feedback for a submission"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT human_score, human_feedback, last_updated, instructor_id
                FROM human_feedback
                WHERE submission_id = ?
            """, (submission_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'score': result['human_score'],
                    'feedback': result['human_feedback'],
                    'last_updated': result['last_updated'],
                    'instructor_id': result['instructor_id']
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting human feedback for submission {submission_id}: {e}")
            return None
    
    def save_human_feedback(self, submission_id: int, score: float, feedback: str, instructor_id: str = "instructor") -> bool:
        """
        Save human feedback for a submission - SINGLE SOURCE OF TRUTH
        
        Data Flow:
        1. Primary storage: human_feedback table (authoritative source)
        2. Update submissions.final_score for quick access (derived field)
        3. Keep submissions.human_score/human_feedback for backward compatibility only
        """
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()
            
            # Validate score range
            if not (0 <= score <= 37.5):
                st.error("Score must be between 0 and 37.5")
                return False
            
            # Begin transaction for data consistency
            cursor.execute("BEGIN TRANSACTION")
            
            try:
                # 1. PRIMARY: Insert or update in human_feedback table (authoritative source)
                cursor.execute("""
                    INSERT OR REPLACE INTO human_feedback 
                    (submission_id, human_score, human_feedback, instructor_id, last_updated)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (submission_id, score, feedback, instructor_id))
                
                # 2. DERIVED: Update final_score in submissions table (for quick access)
                cursor.execute("""
                    UPDATE submissions
                    SET final_score = ?
                    WHERE id = ?
                """, (score, submission_id))
                
                # 3. UPDATE instructor_comments in ai_feedback JSON
                cursor.execute("SELECT ai_feedback FROM submissions WHERE id = ?", (submission_id,))
                row = cursor.fetchone()
                if row and row[0]:
                    try:
                        ai_feedback = json.loads(row[0])
                        # Update instructor_comments in comprehensive_feedback
                        if 'comprehensive_feedback' in ai_feedback:
                            if isinstance(ai_feedback['comprehensive_feedback'], dict):
                                ai_feedback['comprehensive_feedback']['instructor_comments'] = feedback
                            elif isinstance(ai_feedback['comprehensive_feedback'], str):
                                comp_feed = json.loads(ai_feedback['comprehensive_feedback'])
                                comp_feed['instructor_comments'] = feedback
                                ai_feedback['comprehensive_feedback'] = comp_feed
                        
                        # Update the ai_feedback field with modified JSON
                        cursor.execute("""
                            UPDATE submissions
                            SET ai_feedback = ?
                            WHERE id = ?
                        """, (json.dumps(ai_feedback), submission_id))
                    except json.JSONDecodeError:
                        logger.warning(f"Could not parse ai_feedback JSON for submission {submission_id}")
                
                # 4. BACKWARD COMPATIBILITY: Update legacy fields in submissions table
                # Note: These are kept for compatibility but human_feedback table is authoritative
                cursor.execute("""
                    UPDATE submissions
                    SET human_score = ?, human_feedback = ?
                    WHERE id = ?
                """, (score, feedback, submission_id))
                
                # Commit transaction
                cursor.execute("COMMIT")
                
                conn.close()
                
                logger.info(f"Saved human feedback for submission {submission_id}: score={score}")
                return True
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e
            
        except Exception as e:
            logger.error(f"Error saving human feedback for submission {submission_id}: {e}")
            st.error(f"Error saving feedback: {e}")
            return False
    
    def get_notebook_content(self, notebook_path: str) -> Optional[Dict[str, Any]]:
        """Get notebook content for display with error handling"""
        try:
            if not notebook_path or not os.path.exists(notebook_path):
                logger.warning(f"Notebook file not found: {notebook_path}")
                return None
            
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook = nbformat.read(f, as_version=4)
            
            # Calculate notebook statistics
            code_cells = [cell for cell in notebook.cells if cell.cell_type == 'code']
            markdown_cells = [cell for cell in notebook.cells if cell.cell_type == 'markdown']
            
            return {
                'notebook': notebook,
                'cell_count': len(notebook.cells),
                'code_cells': len(code_cells),
                'markdown_cells': len(markdown_cells),
                'has_outputs': any(hasattr(cell, 'outputs') and cell.outputs for cell in code_cells)
            }
            
        except Exception as e:
            logger.error(f"Error reading notebook {notebook_path}: {e}")
            st.error(f"Error loading notebook: {e}")
            return None
    
    def get_training_stats(self, assignment_id: int) -> Dict[str, Any]:
        """Get comprehensive training statistics for an assignment"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()
            
            # Get basic statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_submissions,
                    COUNT(hf.id) as human_reviewed,
                    AVG(s.ai_score) as avg_ai_score,
                    AVG(hf.human_score) as avg_human_score,
                    AVG(CASE WHEN hf.human_score IS NOT NULL THEN hf.human_score ELSE s.final_score END) as avg_final_score
                FROM submissions s
                LEFT JOIN human_feedback hf ON s.id = hf.submission_id
                WHERE s.assignment_id = ?
            """, (assignment_id,))
            
            stats = cursor.fetchone()
            
            # Get score distribution
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN COALESCE(hf.human_score, s.final_score) >= 35 THEN 'Excellent (35-37.5)'
                        WHEN COALESCE(hf.human_score, s.final_score) >= 30 THEN 'Good (30-34.9)'
                        WHEN COALESCE(hf.human_score, s.final_score) >= 25 THEN 'Fair (25-29.9)'
                        ELSE 'Needs Work (<25)'
                    END as grade_category,
                    COUNT(*) as count
                FROM submissions s
                LEFT JOIN human_feedback hf ON s.id = hf.submission_id
                WHERE s.assignment_id = ?
                GROUP BY grade_category
            """, (assignment_id,))
            
            distribution = dict(cursor.fetchall())
            
            # Get AI accuracy metrics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_reviewed,
                    COUNT(CASE WHEN ABS(s.ai_score - hf.human_score) <= 2.0 THEN 1 END) as within_2_points,
                    AVG(ABS(s.ai_score - hf.human_score)) as avg_difference
                FROM submissions s
                JOIN human_feedback hf ON s.id = hf.submission_id
                WHERE s.assignment_id = ?
            """, (assignment_id,))
            
            accuracy_stats = cursor.fetchone()
            
            conn.close()
            
            # Calculate derived metrics
            total_submissions = stats['total_submissions'] or 0
            human_reviewed = stats['human_reviewed'] or 0
            review_percentage = (human_reviewed / max(total_submissions, 1)) * 100
            
            ai_accuracy = 0
            if accuracy_stats and accuracy_stats['total_reviewed'] > 0:
                ai_accuracy = (accuracy_stats['within_2_points'] / accuracy_stats['total_reviewed']) * 100
            
            return {
                'total_submissions': total_submissions,
                'human_reviewed': human_reviewed,
                'review_percentage': round(review_percentage, 1),
                'avg_ai_score': round(stats['avg_ai_score'] or 0, 1),
                'avg_human_score': round(stats['avg_human_score'] or 0, 1),
                'avg_final_score': round(stats['avg_final_score'] or 0, 1),
                'score_distribution': distribution,
                'ai_accuracy_percentage': round(ai_accuracy, 1),
                'avg_score_difference': round(accuracy_stats['avg_difference'] or 0, 1) if accuracy_stats else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting training stats for assignment {assignment_id}: {e}")
            return {
                'total_submissions': 0,
                'human_reviewed': 0,
                'review_percentage': 0,
                'avg_ai_score': 0,
                'avg_human_score': 0,
                'avg_final_score': 0,
                'score_distribution': {},
                'ai_accuracy_percentage': 0,
                'avg_score_difference': 0
            }
    
    def apply_bulk_operation(self, submission_ids: List[int], operation: str, **kwargs) -> Tuple[bool, str]:
        """Apply bulk operations to multiple submissions"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()
            
            success_count = 0
            
            for submission_id in submission_ids:
                try:
                    if operation == "boost_percentage":
                        boost_percent = kwargs.get('boost_percent', 5)
                        # Get current AI score
                        cursor.execute("""
                            SELECT ai_score
                            FROM submissions
                            WHERE id = ?
                        """, (submission_id,))
                        
                        result = cursor.fetchone()
                        if result:
                            current_score = result['ai_score']
                            new_score = min(37.5, current_score * (1 + boost_percent / 100))
                            
                            if self.save_human_feedback(submission_id, new_score, f"Boosted by {boost_percent}%"):
                                success_count += 1
                    
                    elif operation == "reset_to_ai":
                        # Reset to AI score - maintain data consistency
                        cursor.execute("BEGIN TRANSACTION")
                        try:
                            # 1. Remove from authoritative human_feedback table
                            cursor.execute("DELETE FROM human_feedback WHERE submission_id = ?", (submission_id,))
                            
                            # 2. Reset final_score to AI score in submissions table
                            cursor.execute("""
                                UPDATE submissions 
                                SET final_score = COALESCE(ai_score, 0)
                                WHERE id = ?
                            """, (submission_id,))
                            
                            # 3. Clear backward compatibility fields
                            cursor.execute("""
                                UPDATE submissions 
                                SET human_score = NULL, human_feedback = NULL
                                WHERE id = ?
                            """, (submission_id,))
                            
                            cursor.execute("COMMIT")
                            success_count += 1
                        except Exception as e:
                            cursor.execute("ROLLBACK")
                            logger.error(f"Error resetting submission {submission_id}: {e}")
                            continue
                    
                    elif operation == "apply_curve":
                        curve_points = kwargs.get('curve_points', 2)
                        # Get current final score
                        cursor.execute("""
                            SELECT COALESCE(hf.human_score, s.final_score) as current_score
                            FROM submissions s
                            LEFT JOIN human_feedback hf ON s.id = hf.submission_id
                            WHERE s.id = ?
                        """, (submission_id,))
                        
                        result = cursor.fetchone()
                        if result:
                            current_score = result['current_score']
                            new_score = min(37.5, current_score + curve_points)
                            
                            if self.save_human_feedback(submission_id, new_score, f"Curve applied (+{curve_points} points)"):
                                success_count += 1
                
                except Exception as e:
                    logger.error(f"Error applying {operation} to submission {submission_id}: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            message = f"Successfully applied {operation} to {success_count}/{len(submission_ids)} submissions"
            logger.info(message)
            return True, message
            
        except Exception as e:
            logger.error(f"Error in bulk operation {operation}: {e}")
            return False, f"Bulk operation failed: {e}"
    
    def export_to_csv(self, assignment_id: int, submissions: List[Dict]) -> Optional[str]:
        """Export grading data to CSV format"""
        try:
            # Prepare data for CSV
            csv_data = []
            for submission in submissions:
                csv_data.append({
                    'Student Name': submission['student_name'],
                    'Student ID': submission['student_id'],
                    'AI Score': submission['ai_score'],
                    'Human Score': submission['human_score'] or '',
                    'Final Score': submission['final_score'],
                    'AI Percentage': submission['ai_percentage'],
                    'Final Percentage': (submission['final_score'] / 37.5) * 100,
                    'Score Status': submission['score_status'],
                    'Grade Category': submission['grade_category'],
                    'Submission Date': submission['submission_date'],
                    'Review Date': submission['review_date'] or '',
                    'Grading Method': submission['grading_method'] or '',
                    'Human Feedback': (submission['human_feedback'] or '')[:200]  # Truncate feedback
                })
            
            df = pd.DataFrame(csv_data)
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
            df.to_csv(temp_file.name, index=False)
            temp_file.close()
            
            logger.info(f"Exported {len(csv_data)} submissions to CSV")
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            st.error(f"CSV export failed: {e}")
            return None
    
    def generate_clean_pdf_report(self, submission_id: int, student_name: str, assignment_name: str) -> Optional[str]:
        """
        Generate a clean PDF report with only instructor-relevant content
        
        This is the ONLY PDF generation method - no express versions
        """
        try:
            from report_generator import PDFReportGenerator
            from validate_report_content import ReportContentValidator
            
            # Get submission data
            conn = self.get_database_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.*, s.ai_feedback as comprehensive_feedback, s.ai_score,
                       hf.human_score, hf.human_feedback
                FROM submissions s
                LEFT JOIN human_feedback hf ON s.id = hf.submission_id
                WHERE s.id = ?
            """, (submission_id,))
            
            submission_data = cursor.fetchone()
            conn.close()
            
            if not submission_data:
                st.error("Submission not found")
                return None
            
            # Prepare analysis result
            analysis_result = {
                'total_score': submission_data['human_score'] or submission_data['ai_score'] or 0,
                'max_score': 37.5,
                'element_scores': {},
                'detailed_feedback': [],
                'code_issues': [],
                'question_analysis': {}
            }
            
            # Parse AI feedback if available
            if submission_data['comprehensive_feedback']:
                try:
                    ai_feedback = json.loads(submission_data['comprehensive_feedback'])
                    
                    # Validate and clean the feedback content
                    validator = ReportContentValidator()
                    is_valid, issues = validator.validate_feedback_content(ai_feedback)
                    
                    if not is_valid:
                        logger.warning(f"Cleaning feedback content for submission {submission_id}: {issues}")
                    
                    # Clean the feedback for instructor use
                    if 'instructor_comments' in ai_feedback:
                        ai_feedback['instructor_comments'] = validator.clean_feedback_for_instructor(
                            ai_feedback['instructor_comments']
                        )
                    
                    # Clean detailed feedback sections
                    if 'detailed_feedback' in ai_feedback:
                        for section_name, section_content in ai_feedback['detailed_feedback'].items():
                            if isinstance(section_content, list):
                                cleaned_items = []
                                for item in section_content:
                                    cleaned_item = validator.clean_feedback_for_instructor(item)
                                    if cleaned_item and len(cleaned_item) > 15:
                                        cleaned_items.append(cleaned_item)
                                ai_feedback['detailed_feedback'][section_name] = cleaned_items
                    
                    analysis_result['comprehensive_feedback'] = ai_feedback
                    
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse AI feedback for submission {submission_id}")
                    # Generate fallback feedback
                    validator = ReportContentValidator()
                    fallback_feedback = validator.generate_instructor_fallback(
                        analysis_result['total_score'], 
                        analysis_result['max_score']
                    )
                    analysis_result['comprehensive_feedback'] = {
                        'instructor_comments': fallback_feedback
                    }
            
            # Add human feedback if available
            if submission_data['human_feedback']:
                validator = ReportContentValidator()
                clean_human_feedback = validator.clean_feedback_for_instructor(
                    submission_data['human_feedback']
                )
                
                # Add human feedback to the report
                if 'comprehensive_feedback' not in analysis_result:
                    analysis_result['comprehensive_feedback'] = {}
                
                # Prepend human feedback to instructor comments
                existing_comments = analysis_result['comprehensive_feedback'].get('instructor_comments', '')
                human_section = f"Instructor Review: {clean_human_feedback}"
                
                if existing_comments:
                    analysis_result['comprehensive_feedback']['instructor_comments'] = f"{human_section}\n\n{existing_comments}"
                else:
                    analysis_result['comprehensive_feedback']['instructor_comments'] = human_section
            
            # Generate the PDF report
            report_generator = PDFReportGenerator()
            pdf_path = report_generator.generate_report(
                student_name=student_name,
                assignment_id=assignment_name,
                analysis_result=analysis_result
            )
            
            logger.info(f"Generated clean PDF report for {student_name}: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Error generating PDF report for submission {submission_id}: {e}")
            st.error(f"Error generating PDF report: {e}")
            return None
    
    def validate_and_fix_data_consistency(self) -> Dict[str, Any]:
        """
        Validate and fix data consistency across all tables
        
        Returns:
            Dict with validation results
        """
        try:
            from enhanced_training_database import EnhancedTrainingDatabase
            
            db = EnhancedTrainingDatabase(self.db_path)
            results = db.validate_data_consistency()
            
            logger.info(f"Data validation completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error during data validation: {e}")
            return {
                'issues_found': [f"Validation failed: {e}"],
                'fixes_applied': [],
                'total_submissions': 0,
                'consistent_records': 0
            }

def display_interactive_notebook(notebook_content: Dict[str, Any], view_mode: str = "full"):
    """Display notebook content with different view modes"""
    
    if not notebook_content:
        st.error("Unable to load notebook content")
        return
    
    notebook = notebook_content['notebook']
    
    if view_mode == "summary":
        # Summary mode - overview with metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Cells", notebook_content['cell_count'])
        with col2:
            st.metric("Code Cells", notebook_content['code_cells'])
        with col3:
            st.metric("Markdown Cells", notebook_content['markdown_cells'])
        
        st.subheader("Notebook Overview")
        for i, cell in enumerate(notebook.cells[:5]):  # Show first 5 cells
            with st.expander(f"Cell {i+1} ({cell.cell_type})"):
                if cell.cell_type == 'code':
                    st.code(cell.source, language='python')
                else:
                    st.markdown(cell.source)
        
        if len(notebook.cells) > 5:
            st.info(f"... and {len(notebook.cells) - 5} more cells")
    
    elif view_mode == "code_only":
        # Code only mode - simple code view
        st.subheader("Code Cells Only")
        code_cells = [cell for cell in notebook.cells if cell.cell_type == 'code']
        
        for i, cell in enumerate(code_cells):
            st.subheader(f"Code Cell {i+1}")
            st.code(cell.source, language='python')
            
            # Show outputs if available
            if hasattr(cell, 'outputs') and cell.outputs:
                st.caption("Output:")
                for output in cell.outputs:
                    if output.output_type == 'stream':
                        st.text(output.text)
                    elif output.output_type == 'execute_result':
                        if 'text/plain' in output.data:
                            st.text(output.data['text/plain'])
    
    else:  # full interactive mode
        # Full interactive mode - all cells with proper formatting
        st.subheader("Full Notebook View")
        
        for i, cell in enumerate(notebook.cells):
            st.markdown(f"**Cell {i+1} ({cell.cell_type})**")
            
            if cell.cell_type == 'code':
                st.code(cell.source, language='python')
                
                # Display outputs
                if hasattr(cell, 'outputs') and cell.outputs:
                    st.caption("Output:")
                    for output in cell.outputs:
                        if output.output_type == 'stream':
                            st.text(output.text)
                        elif output.output_type == 'execute_result':
                            if 'text/html' in output.data:
                                st.markdown(output.data['text/html'], unsafe_allow_html=True)
                            elif 'text/plain' in output.data:
                                st.text(output.data['text/plain'])
                        elif output.output_type == 'display_data':
                            if 'image/png' in output.data:
                                st.image(output.data['image/png'])
                            elif 'text/html' in output.data:
                                st.markdown(output.data['text/html'], unsafe_allow_html=True)
                        elif output.output_type == 'error':
                            st.error(f"Error: {output.ename}: {output.evalue}")
                            st.code('\n'.join(output.traceback), language='python')
            
            elif cell.cell_type == 'markdown':
                st.markdown(cell.source)
            
            st.markdown("---")