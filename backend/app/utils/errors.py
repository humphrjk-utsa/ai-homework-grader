"""Centralized error handlers for the Flask API."""
from flask import jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.orm.exc import StaleDataError


def register_error_handlers(app):
    """Register error handlers on the Flask app."""

    @app.errorhandler(StaleDataError)
    def stale_data(e):
        from app.extensions import db
        db.session.rollback()
        return jsonify(
            error='Conflict: this record was modified by another user. Please refresh and try again.'
        ), 409

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(error='Bad request', message=str(e.description)), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify(error='Unauthorized', message='Authentication required'), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify(error='Forbidden', message=str(e.description)), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error='Not found', message=str(e.description)), 404

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify(error='Unprocessable entity', message=str(e.description)), 422

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify(error='Internal server error', message='An unexpected error occurred'), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify(error=e.name, message=str(e.description)), e.code
