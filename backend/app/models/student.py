"""Student and CourseEnrollment models."""
from datetime import datetime

from app.extensions import db


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    canvas_id = db.Column(db.String(50))
    student_id_external = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('organization_id', 'canvas_id', name='uq_student_canvas'),
    )

    enrollments = db.relationship('CourseEnrollment', backref='student', lazy='dynamic')
    submissions = db.relationship('Submission', backref='student', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'canvas_id': self.canvas_id,
            'student_id_external': self.student_id_external,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class CourseEnrollment(db.Model):
    __tablename__ = 'course_enrollments'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')

    __table_args__ = (
        db.UniqueConstraint('course_id', 'student_id', name='uq_enrollment'),
    )
