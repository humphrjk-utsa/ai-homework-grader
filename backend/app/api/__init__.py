"""Register all API blueprints."""


def register_blueprints(app):
    from app.api.auth import auth_bp
    from app.api.courses import courses_bp
    from app.api.assignments import assignments_bp
    from app.api.students import students_bp
    from app.api.submissions import submissions_bp
    from app.api.grading import grading_bp
    from app.api.reports import reports_bp
    from app.api.health import health_bp
    from app.api.canvas import canvas_bp
    from app.api.rag import rag_bp
    from app.api.training import training_bp
    from app.api.models import models_bp
    from app.api.ground_truth import ground_truth_bp
    from app.api.playground import playground_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(courses_bp, url_prefix='/api')
    app.register_blueprint(assignments_bp, url_prefix='/api')
    app.register_blueprint(students_bp, url_prefix='/api')
    app.register_blueprint(submissions_bp, url_prefix='/api')
    app.register_blueprint(grading_bp, url_prefix='/api/grading')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(canvas_bp, url_prefix='/api/canvas')
    app.register_blueprint(rag_bp, url_prefix='/api/rag')
    app.register_blueprint(training_bp, url_prefix='/api/training')
    app.register_blueprint(models_bp, url_prefix='/api/models')
    app.register_blueprint(ground_truth_bp, url_prefix='/api')
    app.register_blueprint(playground_bp, url_prefix='/api/playground')
