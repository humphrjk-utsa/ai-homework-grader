"""Assignment model."""
from datetime import datetime

from app.extensions import db


class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    assignment_type = db.Column(db.String(20), nullable=False, default='coding')
    total_points = db.Column(db.Float, nullable=False, default=37.5)
    language = db.Column(db.String(20), default='R')

    # File paths (relative to storage/{org}/{course}/assignments/{slug}/)
    rubric_path = db.Column(db.String(500))
    solution_path = db.Column(db.String(500))
    template_path = db.Column(db.String(500))

    # Grading configuration
    grading_config = db.Column(db.JSON, default=dict)
    code_analysis_prompt = db.Column(db.Text)
    feedback_prompt = db.Column(db.Text)

    canvas_assignment_id = db.Column(db.String(50))
    due_date = db.Column(db.DateTime)
    is_published = db.Column(db.Boolean, default=False)
    version = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __mapper_args__ = {
        'version_id_col': version,
    }

    __table_args__ = (
        db.UniqueConstraint('course_id', 'slug', name='uq_assignment_course_slug'),
    )

    submissions = db.relationship('Submission', backref='assignment', lazy='dynamic',
                                  cascade='all, delete-orphan')

    def to_dict(self, include_stats=False):
        d = {
            'id': self.id,
            'course_id': self.course_id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'assignment_type': self.assignment_type,
            'total_points': self.total_points,
            'language': self.language,
            'rubric_path': self.rubric_path,
            'solution_path': self.solution_path,
            'template_path': self.template_path,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'code_analysis_prompt': self.code_analysis_prompt,
            'feedback_prompt': self.feedback_prompt,
            'grading_config': self.grading_config,
            'version': self.version,
        }
        if include_stats:
            from app.models.submission import Submission
            total = self.submissions.count()
            graded = self.submissions.filter(Submission.status == 'graded').count()
            d['total_submissions'] = total
            d['graded_submissions'] = graded
        return d
