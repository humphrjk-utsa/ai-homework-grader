"""Report and ReportTemplate models."""
from datetime import datetime

from app.extensions import db


class ReportTemplate(db.Model):
    __tablename__ = 'report_templates'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    template_config = db.Column(db.JSON, default=dict)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    courses = db.relationship('Course', backref='report_template', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'template_config': self.template_config,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('report_templates.id'))
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    generated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    generated_by = db.relationship('User', backref='generated_reports')

    def to_dict(self):
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
        }
