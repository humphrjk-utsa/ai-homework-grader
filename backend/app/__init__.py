"""Flask application factory."""
import os
import sys

from flask import Flask

from app.config import config_map
from app.extensions import db, migrate, jwt, cors

# Add project root to sys.path so engine/ package is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def create_app(config_name=None):
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {"origins": app.config['CORS_ORIGINS']}
    })

    # Initialize Celery (safe to call even without Redis)
    from app.tasks.celery_app import init_celery
    init_celery(app)

    # Ensure storage directory exists
    os.makedirs(app.config['STORAGE_ROOT'], exist_ok=True)

    # Import all models so Alembic can detect them
    from app.models import user, course, assignment, student, submission, grading_job, report  # noqa: F401

    # Register blueprints
    from app.api import register_blueprints
    register_blueprints(app)

    # Register middleware
    from app.middleware.tenant import inject_tenant_context
    app.before_request(inject_tenant_context)

    # Register error handlers
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)

    return app
