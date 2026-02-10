"""Submission model."""
from datetime import datetime

from app.extensions import db


class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)

    # File info
    original_filename = db.Column(db.String(500))
    file_path = db.Column(db.String(500))
    file_type = db.Column(db.String(20))

    # Grading results
    ai_score = db.Column(db.Float)
    ai_feedback = db.Column(db.JSON)
    human_score = db.Column(db.Float)
    human_feedback = db.Column(db.Text)
    final_score = db.Column(db.Float)
    max_score = db.Column(db.Float)

    # Component breakdown
    component_scores = db.Column(db.JSON)
    component_percentages = db.Column(db.JSON)
    validation_results = db.Column(db.JSON)

    # Status tracking
    status = db.Column(db.String(20), default='uploaded')
    grading_job_id = db.Column(db.Integer, db.ForeignKey('grading_jobs.id'))
    error_message = db.Column(db.Text)

    # Timestamps
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    graded_at = db.Column(db.DateTime)
    reviewed_at = db.Column(db.DateTime)

    # Preprocessing info
    preprocessing_info = db.Column(db.JSON)
    execution_info = db.Column(db.JSON)

    __table_args__ = (
        db.UniqueConstraint('assignment_id', 'student_id', name='uq_submission'),
    )

    reports = db.relationship('Report', backref='submission', lazy='dynamic')

    def to_dict(self, include_feedback=False):
        d = {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'status': self.status,
            'ai_score': self.ai_score,
            'human_score': self.human_score,
            'final_score': self.final_score,
            'max_score': self.max_score,
            'file_path': self.file_path,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'error_message': self.error_message,
        }
        if include_feedback:
            d['ai_feedback'] = self.ai_feedback
            d['component_scores'] = self.component_scores
            d['component_percentages'] = self.component_percentages
            d['validation_results'] = self.validation_results
            d['human_feedback'] = self.human_feedback
        return d
