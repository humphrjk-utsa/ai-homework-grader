"""GradingJob model for async batch tracking."""
from datetime import datetime

from app.extensions import db


class GradingJob(db.Model):
    __tablename__ = 'grading_jobs'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    status = db.Column(db.String(20), default='pending')
    job_type = db.Column(db.String(20), default='batch')

    # Progress
    total_submissions = db.Column(db.Integer, default=0)
    completed_submissions = db.Column(db.Integer, default=0)
    failed_submissions = db.Column(db.Integer, default=0)
    progress_percent = db.Column(db.Float, default=0.0)

    # Celery tracking
    celery_task_id = db.Column(db.String(255))

    # Metrics
    performance_metrics = db.Column(db.JSON, default=dict)
    grading_config = db.Column(db.JSON, default=dict)
    error_message = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    # Relationships
    created_by = db.relationship('User', backref='grading_jobs')
    assignment = db.relationship('Assignment', backref='grading_jobs')
    submissions = db.relationship('Submission', backref='grading_job', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'status': self.status,
            'job_type': self.job_type,
            'total_submissions': self.total_submissions,
            'completed_submissions': self.completed_submissions,
            'failed_submissions': self.failed_submissions,
            'progress_percent': self.progress_percent,
            'performance_metrics': self.performance_metrics,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
