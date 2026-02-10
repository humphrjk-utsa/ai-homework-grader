"""Model management API endpoints."""
from flask import Blueprint, jsonify, request, g, current_app

from app.utils.decorators import tenant_required
from app.extensions import db

models_bp = Blueprint('models', __name__)


def _get_model_service():
    from app.services.model_service import ModelService
    return ModelService(current_app.config['STORAGE_ROOT'])


@models_bp.route('', methods=['GET'])
@tenant_required
def list_models():
    """List all available models (built-in + custom)."""
    course_id = request.args.get('course_id', type=int)
    svc = _get_model_service()
    models = svc.list_models(g.organization_id, course_id=course_id)
    return jsonify(models=models)


@models_bp.route('', methods=['POST'])
@tenant_required
def register_model():
    """Register a new custom model."""
    data = request.get_json() or {}

    if not data.get('name') or not data.get('model_id'):
        return jsonify(error='name and model_id are required'), 400

    svc = _get_model_service()
    model = svc.register_model(g.organization_id, data)
    return jsonify(model=model.to_dict()), 201


@models_bp.route('/<int:model_id>/deploy', methods=['POST'])
@tenant_required
def deploy_model(model_id):
    """Deploy a model as a vLLM Docker container."""
    from app.models.training import CustomModel

    model = db.session.get(CustomModel, model_id)
    if not model or model.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    config = request.get_json() or {}
    svc = _get_model_service()

    try:
        result = svc.deploy_model(model_id, config)
        return jsonify(result=result)
    except RuntimeError as e:
        return jsonify(error=str(e)), 500


@models_bp.route('/<int:model_id>/stop', methods=['POST'])
@tenant_required
def stop_model(model_id):
    """Stop a running model container."""
    from app.models.training import CustomModel

    model = db.session.get(CustomModel, model_id)
    if not model or model.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    svc = _get_model_service()
    result = svc.stop_model(model_id)
    return jsonify(result=result)


@models_bp.route('/running', methods=['GET'])
@tenant_required
def running_models():
    """Get all currently running model containers."""
    svc = _get_model_service()
    models = svc.get_running_models(g.organization_id)
    return jsonify(models=models)


@models_bp.route('/course-config/<int:course_id>', methods=['PUT'])
@tenant_required
def set_course_model_config(course_id):
    """Set which models a course uses for grading."""
    from app.models.course import Course

    course = db.session.get(Course, course_id)
    if not course or course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    data = request.get_json() or {}
    svc = _get_model_service()
    settings = svc.set_course_model_config(course_id, data)
    return jsonify(settings=settings)
