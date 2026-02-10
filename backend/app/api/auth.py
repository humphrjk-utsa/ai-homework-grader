"""Authentication endpoints: register, login, refresh, profile."""
import re
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)

from app.extensions import db
from app.models.user import Organization, User

auth_bp = Blueprint('auth', __name__)


def _slugify(text):
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[\s_]+', '-', text)[:100]


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user. First user of an org becomes admin."""
    data = request.get_json() or {}

    required = ['email', 'password', 'first_name', 'last_name', 'organization_name']
    for field in required:
        if not data.get(field):
            return jsonify(error=f'{field} is required'), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify(error='Email already registered'), 409

    org_slug = _slugify(data['organization_name'])
    org = Organization.query.filter_by(slug=org_slug).first()

    if org is None:
        org = Organization(name=data['organization_name'], slug=org_slug)
        db.session.add(org)
        db.session.flush()
        role = 'admin'
    else:
        role = 'instructor'

    user = User(
        organization_id=org.id,
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        role=role,
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify(
        user=user.to_dict(),
        access_token=access_token,
        refresh_token=refresh_token,
    ), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with email and password, returns JWT tokens."""
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify(error='Email and password required'), 400

    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return jsonify(error='Invalid email or password'), 401

    if not user.is_active:
        return jsonify(error='Account is disabled'), 403

    user.last_login = datetime.now(timezone.utc)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify(
        user=user.to_dict(),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Get a new access token using a refresh token."""
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify(access_token=access_token)


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile."""
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id)) or abort(404)
    return jsonify(user=user.to_dict())


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile."""
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id)) or abort(404)
    data = request.get_json() or {}

    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'password' in data and data['password']:
        user.set_password(data['password'])

    db.session.commit()
    return jsonify(user=user.to_dict())
