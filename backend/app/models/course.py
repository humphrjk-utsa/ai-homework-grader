"""Course and CourseMembership models."""
from datetime import datetime

from app.extensions import db


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50))
    semester = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    canvas_course_id = db.Column(db.String(50))
    report_template_id = db.Column(db.Integer, db.ForeignKey('report_templates.id'))
    settings = db.Column(db.JSON, default=dict)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('organization_id', 'slug', name='uq_course_org_slug'),
    )

    assignments = db.relationship('Assignment', backref='course', lazy='dynamic',
                                  cascade='all, delete-orphan')
    enrollments = db.relationship('CourseEnrollment', backref='course', lazy='dynamic',
                                  cascade='all, delete-orphan')
    members = db.relationship('CourseMembership', backref='course', lazy='dynamic',
                              cascade='all, delete-orphan')

    def to_dict(self, include_stats=False):
        d = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'semester': self.semester,
            'year': self.year,
            'slug': self.slug,
            'owner_id': self.owner_id,
            'is_active': self.is_active,
            'settings': self.settings,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_stats:
            d['assignment_count'] = self.assignments.count()
            d['student_count'] = self.enrollments.filter_by(status='active').count()
        return d


class CourseMembership(db.Model):
    __tablename__ = 'course_memberships'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='ta')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('course_id', 'user_id', name='uq_course_member'),
    )
