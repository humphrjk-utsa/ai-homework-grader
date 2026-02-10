"""Canvas LMS integration endpoints."""
import os
import logging
import requests as http_requests

from flask import Blueprint, request, jsonify, g, current_app

from app.extensions import db
from app.models.user import Organization
from app.models.course import Course
from app.models.student import Student, CourseEnrollment
from app.models.assignment import Assignment
from app.models.submission import Submission
from app.utils.decorators import role_required

logger = logging.getLogger(__name__)

canvas_bp = Blueprint('canvas', __name__)


def _get_canvas_config():
    """Read Canvas URL + token from the current org's settings."""
    org = Organization.query.get(g.organization_id)
    settings = org.settings or {}
    return settings.get('canvas_url'), settings.get('canvas_api_token')


def _get_canvas_service():
    """Build a CanvasService from org settings."""
    url, token = _get_canvas_config()
    if not url or not token:
        return None
    from app.services.canvas_service import CanvasService
    return CanvasService(url, token)


# ------------------------------------------------------------------
# Settings
# ------------------------------------------------------------------

@canvas_bp.route('/settings', methods=['GET'])
@role_required('admin', 'instructor')
def get_settings():
    """Get Canvas connection settings (URL only, never expose token)."""
    url, token = _get_canvas_config()
    return jsonify(
        canvas_url=url or '',
        has_token=bool(token),
    )


@canvas_bp.route('/settings', methods=['PUT'])
@role_required('admin', 'instructor')
def update_settings():
    """Save Canvas URL and API token."""
    data = request.get_json() or {}
    org = Organization.query.get(g.organization_id)
    settings = dict(org.settings or {})

    if 'canvas_url' in data:
        url = data['canvas_url'].rstrip('/')
        settings['canvas_url'] = url
    if 'canvas_api_token' in data:
        settings['canvas_api_token'] = data['canvas_api_token']

    org.settings = settings
    db.session.commit()
    return jsonify(message='Canvas settings saved')


@canvas_bp.route('/test', methods=['POST'])
@role_required('admin', 'instructor')
def test_connection():
    """Test Canvas connection."""
    svc = _get_canvas_service()
    if not svc:
        return jsonify(error='Canvas is not configured. Save URL and API token first.'), 400
    try:
        info = svc.test_connection()
        return jsonify(connected=True, user=info)
    except Exception as e:
        return jsonify(connected=False, error=str(e)), 400


# ------------------------------------------------------------------
# Courses
# ------------------------------------------------------------------

@canvas_bp.route('/courses', methods=['GET'])
@role_required('admin', 'instructor')
def list_canvas_courses():
    """List Canvas courses visible to the API token owner."""
    svc = _get_canvas_service()
    if not svc:
        return jsonify(error='Canvas is not configured'), 400
    try:
        courses = svc.list_courses()
        return jsonify(courses=courses)
    except Exception as e:
        return jsonify(error=str(e)), 500


# ------------------------------------------------------------------
# Student sync
# ------------------------------------------------------------------

@canvas_bp.route('/sync/students/<int:course_id>', methods=['POST'])
@role_required('admin', 'instructor')
def sync_students(course_id):
    """Pull students from Canvas into a local course."""
    course = Course.query.filter_by(
        id=course_id, organization_id=g.organization_id
    ).first_or_404()

    if not course.canvas_course_id:
        return jsonify(error='Course has no Canvas course ID linked'), 400

    svc = _get_canvas_service()
    if not svc:
        return jsonify(error='Canvas is not configured'), 400

    try:
        canvas_students = svc.sync_students(int(course.canvas_course_id))
    except Exception as e:
        return jsonify(error=f'Canvas API error: {e}'), 500

    created = 0
    updated = 0

    for cs in canvas_students:
        student = Student.query.filter_by(
            organization_id=g.organization_id,
            canvas_id=cs['canvas_id'],
        ).first()

        if student:
            student.first_name = cs['first_name']
            student.last_name = cs['last_name']
            student.email = cs['email']
            updated += 1
        else:
            student = Student(
                organization_id=g.organization_id,
                canvas_id=cs['canvas_id'],
                first_name=cs['first_name'],
                last_name=cs['last_name'],
                email=cs['email'],
            )
            db.session.add(student)
            db.session.flush()
            created += 1

        # Ensure enrollment
        enrollment = CourseEnrollment.query.filter_by(
            course_id=course.id, student_id=student.id
        ).first()
        if not enrollment:
            db.session.add(CourseEnrollment(
                course_id=course.id,
                student_id=student.id,
            ))

    db.session.commit()
    return jsonify(created=created, updated=updated,
                   total=len(canvas_students))


# ------------------------------------------------------------------
# Push grades
# ------------------------------------------------------------------

@canvas_bp.route('/push-grades/<int:assignment_id>', methods=['POST'])
@role_required('admin', 'instructor')
def push_grades(assignment_id):
    """Push final scores and feedback to Canvas."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    course = assignment.course
    if not course.canvas_course_id:
        return jsonify(error='Course has no Canvas course ID'), 400

    # We need a canvas_assignment_id on the assignment.  For now we
    # look it up from grading_config, or the user can pass it.
    data = request.get_json() or {}
    canvas_assignment_id = data.get('canvas_assignment_id')
    if not canvas_assignment_id:
        config = assignment.grading_config or {}
        canvas_assignment_id = config.get('canvas_assignment_id')
    if not canvas_assignment_id:
        return jsonify(error='No Canvas assignment ID. Set it in grading_config or pass canvas_assignment_id.'), 400

    svc = _get_canvas_service()
    if not svc:
        return jsonify(error='Canvas is not configured'), 400

    # Push grades for graded/reviewed submissions
    graded = assignment.submissions.filter(
        Submission.status.in_(['graded', 'reviewed']),
        Submission.final_score.isnot(None),
    ).all()

    pushed = 0
    errors = []
    for sub in graded:
        student = sub.student
        if not student or not student.canvas_id:
            errors.append(f'Student {sub.student_id}: no Canvas ID')
            continue
        try:
            comment = ''
            if sub.human_feedback:
                comment = sub.human_feedback
            elif sub.ai_feedback and isinstance(sub.ai_feedback, dict):
                comment = sub.ai_feedback.get('comprehensive_feedback', '')[:5000]

            svc.push_grade(
                canvas_course_id=int(course.canvas_course_id),
                canvas_assignment_id=int(canvas_assignment_id),
                canvas_user_id=int(student.canvas_id),
                score=sub.final_score,
                comment=comment,
            )
            pushed += 1
        except Exception as e:
            errors.append(f'Student {student.canvas_id}: {e}')

    return jsonify(pushed=pushed, errors=errors, total=len(graded))
