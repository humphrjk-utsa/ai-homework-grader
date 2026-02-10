"""Custom decorators for authorization and tenant isolation."""
from functools import wraps
from flask import g, abort
from flask_jwt_extended import jwt_required, get_jwt_identity


def tenant_required(f):
    """Ensure request has valid tenant context from JWT."""
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        if not hasattr(g, 'organization_id') or g.organization_id is None:
            abort(403, description='No tenant context')
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """Ensure current user has one of the specified roles."""
    def decorator(f):
        @wraps(f)
        @tenant_required
        def decorated(*args, **kwargs):
            if g.current_user.role not in roles:
                abort(403, description=f'Requires role: {", ".join(roles)}')
            return f(*args, **kwargs)
        return decorated
    return decorator


def course_access_required(f):
    """Ensure current user has access to the course (owner, member, or admin)."""
    @wraps(f)
    @tenant_required
    def decorated(*args, **kwargs):
        from app.models.course import Course, CourseMembership
        course_id = kwargs.get('course_id')
        if course_id is None:
            return f(*args, **kwargs)

        course = Course.query.filter_by(
            id=course_id,
            organization_id=g.organization_id
        ).first_or_404(description='Course not found')

        # Admin sees everything
        if g.current_user.role == 'admin':
            g.course = course
            return f(*args, **kwargs)

        # Owner or member
        if course.owner_id == g.current_user.id:
            g.course = course
            g.course_role = 'owner'
            return f(*args, **kwargs)

        membership = CourseMembership.query.filter_by(
            course_id=course_id,
            user_id=g.current_user.id
        ).first()
        if membership:
            g.course = course
            g.course_role = membership.role
            return f(*args, **kwargs)

        abort(403, description='No access to this course')
    return decorated
