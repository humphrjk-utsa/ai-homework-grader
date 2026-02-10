"""Tenant context middleware - injects organization context from JWT."""
from flask import g, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.extensions import db


def inject_tenant_context():
    """Before each request, set tenant context from JWT if present."""
    g.current_user = None
    g.organization_id = None

    # Skip auth for public endpoints
    if request.endpoint and request.endpoint in (
        'auth.register', 'auth.login', 'health.health_check', 'static'
    ):
        return

    # Skip if no Authorization header
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return

    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        if user_id:
            from app.models.user import User
            user = db.session.get(User, int(user_id))
            if user and user.is_active:
                g.current_user = user
                g.organization_id = user.organization_id
    except Exception:
        # JWT validation failed - will be caught by @jwt_required if needed
        pass
