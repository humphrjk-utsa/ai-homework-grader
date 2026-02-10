"""Course CRUD endpoints."""
import re
from flask import Blueprint, request, jsonify, g

from app.extensions import db
from app.models.course import Course, CourseMembership
from app.utils.decorators import tenant_required, role_required, course_access_required

courses_bp = Blueprint('courses', __name__)


def _slugify(text, semester='', year=''):
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    if semester:
        slug += f'-{semester.lower()}'
    if year:
        slug += f'-{year}'
    return slug[:100]


@courses_bp.route('/courses', methods=['GET'])
@tenant_required
def list_courses():
    """List courses the current user has access to."""
    query = Course.query.filter_by(organization_id=g.organization_id, is_active=True)

    if g.current_user.role != 'admin':
        # Owner or member
        owned = Course.query.filter_by(owner_id=g.current_user.id, is_active=True)
        member_ids = [m.course_id for m in g.current_user.course_memberships.all()]
        member_courses = Course.query.filter(
            Course.id.in_(member_ids),
            Course.is_active == True
        ) if member_ids else Course.query.filter(False)
        query = owned.union(member_courses)

    courses = query.order_by(Course.year.desc(), Course.semester.desc()).all()
    return jsonify(courses=[c.to_dict(include_stats=True) for c in courses])


@courses_bp.route('/courses', methods=['POST'])
@role_required('admin', 'instructor')
def create_course():
    """Create a new course."""
    data = request.get_json() or {}

    for field in ['name', 'semester', 'year']:
        if not data.get(field):
            return jsonify(error=f'{field} is required'), 400

    slug = _slugify(data.get('code', data['name']), data['semester'], str(data['year']))

    existing = Course.query.filter_by(
        organization_id=g.organization_id, slug=slug
    ).first()
    if existing:
        return jsonify(error='A course with this code/semester/year already exists'), 409

    course = Course(
        organization_id=g.organization_id,
        owner_id=g.current_user.id,
        name=data['name'],
        code=data.get('code', ''),
        semester=data['semester'],
        year=int(data['year']),
        slug=slug,
        canvas_course_id=data.get('canvas_course_id'),
        settings=data.get('settings', {}),
    )
    db.session.add(course)
    db.session.commit()

    return jsonify(course=course.to_dict()), 201


@courses_bp.route('/courses/<int:course_id>', methods=['GET'])
@tenant_required
def get_course(course_id):
    """Get course details."""
    course = Course.query.filter_by(
        id=course_id, organization_id=g.organization_id
    ).first_or_404()
    return jsonify(course=course.to_dict(include_stats=True))


@courses_bp.route('/courses/<int:course_id>', methods=['PUT'])
@course_access_required
def update_course(course_id):
    """Update course details."""
    course = g.course

    data = request.get_json() or {}
    for field in ['name', 'code', 'semester', 'canvas_course_id']:
        if field in data:
            setattr(course, field, data[field])
    if 'year' in data:
        course.year = int(data['year'])
    if 'settings' in data:
        course.settings = data['settings']
    if 'is_active' in data:
        course.is_active = data['is_active']

    db.session.commit()
    return jsonify(course=course.to_dict())


@courses_bp.route('/courses/<int:course_id>', methods=['DELETE'])
@role_required('admin', 'instructor')
def delete_course(course_id):
    """Soft-delete a course."""
    course = Course.query.filter_by(
        id=course_id, organization_id=g.organization_id
    ).first_or_404()
    # Only owner or admin can delete
    if g.current_user.role != 'admin' and course.owner_id != g.current_user.id:
        return jsonify(error='Only the course owner can delete this course'), 403
    course.is_active = False
    db.session.commit()
    return jsonify(message='Course deactivated')


@courses_bp.route('/courses/<int:course_id>/members', methods=['POST'])
@tenant_required
def add_member(course_id):
    """Add a TA or co-instructor to a course."""
    course = Course.query.filter_by(
        id=course_id, organization_id=g.organization_id
    ).first_or_404()

    data = request.get_json() or {}
    from app.models.user import User
    user = User.query.filter_by(
        id=data.get('user_id'), organization_id=g.organization_id
    ).first_or_404()

    existing = CourseMembership.query.filter_by(
        course_id=course.id, user_id=user.id
    ).first()
    if existing:
        return jsonify(error='User is already a member'), 409

    membership = CourseMembership(
        course_id=course.id,
        user_id=user.id,
        role=data.get('role', 'ta'),
    )
    db.session.add(membership)
    db.session.commit()

    return jsonify(message='Member added'), 201


@courses_bp.route('/courses/<int:course_id>/stats', methods=['GET'])
@tenant_required
def course_stats(course_id):
    """Get course statistics."""
    course = Course.query.filter_by(
        id=course_id, organization_id=g.organization_id
    ).first_or_404()

    from app.models.submission import Submission
    from app.models.assignment import Assignment

    assignments = course.assignments.all()
    total_submissions = 0
    graded_submissions = 0
    for a in assignments:
        total_submissions += a.submissions.count()
        graded_submissions += a.submissions.filter(Submission.status == 'graded').count()

    return jsonify(
        course_id=course.id,
        assignment_count=len(assignments),
        student_count=course.enrollments.filter_by(status='active').count(),
        total_submissions=total_submissions,
        graded_submissions=graded_submissions,
    )
