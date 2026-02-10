"""Student management endpoints with CSV bulk import."""
import csv
import io

from flask import Blueprint, request, jsonify, g

from app.extensions import db
from app.models.student import Student, CourseEnrollment
from app.models.course import Course
from app.utils.decorators import tenant_required

students_bp = Blueprint('students', __name__)


@students_bp.route('/courses/<int:course_id>/students', methods=['GET'])
@tenant_required
def list_students(course_id):
    """List students enrolled in a course."""
    course = Course.query.filter_by(
        id=course_id, organization_id=g.organization_id
    ).first_or_404()

    enrollments = course.enrollments.filter_by(status='active').all()
    students = [e.student.to_dict() for e in enrollments]
    return jsonify(students=students)


@students_bp.route('/courses/<int:course_id>/students', methods=['POST'])
@tenant_required
def add_student(course_id):
    """Add a single student to a course."""
    course = Course.query.filter_by(
        id=course_id, organization_id=g.organization_id
    ).first_or_404()

    data = request.get_json() or {}
    if not data.get('first_name') or not data.get('last_name'):
        return jsonify(error='first_name and last_name required'), 400

    # Find or create student
    student = None
    if data.get('canvas_id'):
        student = Student.query.filter_by(
            organization_id=g.organization_id, canvas_id=data['canvas_id']
        ).first()
    if student is None and data.get('email'):
        student = Student.query.filter_by(
            organization_id=g.organization_id, email=data['email']
        ).first()

    if student is None:
        student = Student(
            organization_id=g.organization_id,
            canvas_id=data.get('canvas_id'),
            student_id_external=data.get('student_id_external'),
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data.get('email'),
        )
        db.session.add(student)
        db.session.flush()

    # Enroll in course
    existing = CourseEnrollment.query.filter_by(
        course_id=course.id, student_id=student.id
    ).first()
    if existing:
        existing.status = 'active'
    else:
        enrollment = CourseEnrollment(course_id=course.id, student_id=student.id)
        db.session.add(enrollment)

    db.session.commit()
    return jsonify(student=student.to_dict()), 201


@students_bp.route('/courses/<int:course_id>/students/import', methods=['POST'])
@tenant_required
def import_students(course_id):
    """Bulk import students from CSV file.

    Expected CSV columns: first_name, last_name, email, canvas_id (optional)
    """
    course = Course.query.filter_by(
        id=course_id, organization_id=g.organization_id
    ).first_or_404()

    if 'file' not in request.files:
        return jsonify(error='No CSV file provided'), 400

    file = request.files['file']
    content = file.read().decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(content))

    imported = 0
    skipped = 0
    errors = []

    for i, row in enumerate(reader, start=2):
        first_name = row.get('first_name', '').strip()
        last_name = row.get('last_name', '').strip()
        email = row.get('email', '').strip()
        canvas_id = row.get('canvas_id', '').strip() or None

        if not first_name or not last_name:
            errors.append(f'Row {i}: missing first_name or last_name')
            continue

        # Find or create
        student = None
        if canvas_id:
            student = Student.query.filter_by(
                organization_id=g.organization_id, canvas_id=canvas_id
            ).first()
        if student is None and email:
            student = Student.query.filter_by(
                organization_id=g.organization_id, email=email
            ).first()

        if student is None:
            student = Student(
                organization_id=g.organization_id,
                canvas_id=canvas_id,
                first_name=first_name,
                last_name=last_name,
                email=email or None,
            )
            db.session.add(student)
            db.session.flush()

        # Enroll
        existing = CourseEnrollment.query.filter_by(
            course_id=course.id, student_id=student.id
        ).first()
        if existing:
            skipped += 1
        else:
            db.session.add(CourseEnrollment(course_id=course.id, student_id=student.id))
            imported += 1

    db.session.commit()

    return jsonify(
        imported=imported,
        skipped=skipped,
        errors=errors,
    )


@students_bp.route('/students/<int:student_id>', methods=['GET'])
@tenant_required
def get_student(student_id):
    """Get student details."""
    student = Student.query.filter_by(
        id=student_id, organization_id=g.organization_id
    ).first_or_404()
    return jsonify(student=student.to_dict())


@students_bp.route('/students/<int:student_id>', methods=['PUT'])
@tenant_required
def update_student(student_id):
    """Update student details."""
    student = Student.query.filter_by(
        id=student_id, organization_id=g.organization_id
    ).first_or_404()

    data = request.get_json() or {}
    for field in ['first_name', 'last_name', 'email', 'canvas_id', 'student_id_external']:
        if field in data:
            setattr(student, field, data[field])

    db.session.commit()
    return jsonify(student=student.to_dict())
