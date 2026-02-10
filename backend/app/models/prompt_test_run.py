"""Prompt test run model for the testing playground."""
from datetime import datetime

from app.extensions import db


class PromptTestRun(db.Model):
    __tablename__ = 'prompt_test_runs'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Run configuration
    run_type = db.Column(db.String(20), nullable=False)  # single | sample | comparison
    label = db.Column(db.String(200))

    # Prompt snapshot (frozen at run time)
    code_analysis_prompt = db.Column(db.Text)
    feedback_prompt = db.Column(db.Text)

    # Version B prompts (comparison runs only)
    comparison_code_analysis_prompt = db.Column(db.Text)
    comparison_feedback_prompt = db.Column(db.Text)

    # Input submissions
    submission_ids = db.Column(db.JSON)  # list of int

    # Results
    results = db.Column(db.JSON)
    status = db.Column(db.String(20), default='pending')  # pending | running | completed | error
    error_message = db.Column(db.Text)

    # Performance
    total_duration_seconds = db.Column(db.Float)
    grading_stats = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    assignment = db.relationship('Assignment', backref='prompt_test_runs')
    created_by = db.relationship('User', backref='prompt_test_runs')

    def to_dict(self):
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'created_by_id': self.created_by_id,
            'run_type': self.run_type,
            'label': self.label,
            'code_analysis_prompt': self.code_analysis_prompt,
            'feedback_prompt': self.feedback_prompt,
            'comparison_code_analysis_prompt': self.comparison_code_analysis_prompt,
            'comparison_feedback_prompt': self.comparison_feedback_prompt,
            'submission_ids': self.submission_ids,
            'results': self.results,
            'status': self.status,
            'error_message': self.error_message,
            'total_duration_seconds': self.total_duration_seconds,
            'grading_stats': self.grading_stats,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
