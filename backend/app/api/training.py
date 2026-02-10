"""Training pipeline API endpoints."""
from flask import Blueprint, jsonify, request, g, current_app

from app.utils.decorators import tenant_required
from app.models.training import TrainingJob
from app.models.course import Course
from app.extensions import db

training_bp = Blueprint('training', __name__)


def _get_training_service():
    from app.services.training_service import TrainingService
    return TrainingService(current_app.config['STORAGE_ROOT'])


@training_bp.route('/courses/<int:course_id>/stats', methods=['GET'])
@tenant_required
def get_training_stats(course_id):
    """Get training data statistics for a course."""
    course = Course.query.get_or_404(course_id)
    if course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    svc = _get_training_service()
    stats = svc.get_training_stats(course_id)
    return jsonify(stats=stats)


@training_bp.route('/courses/<int:course_id>/export', methods=['POST'])
@tenant_required
def export_training_data(course_id):
    """Export reviewed submissions as JSONL for fine-tuning."""
    course = Course.query.get_or_404(course_id)
    if course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    svc = _get_training_service()
    result = svc.export_training_data(course_id)

    if result['num_samples'] == 0:
        return jsonify(error='No reviewed submissions with edited feedback found'), 400

    return jsonify(result=result)


@training_bp.route('/courses/<int:course_id>/preview', methods=['GET'])
@tenant_required
def preview_training_data(course_id):
    """Preview a few training data samples."""
    course = Course.query.get_or_404(course_id)
    if course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    svc = _get_training_service()
    previews = svc.get_sample_preview(course_id)
    return jsonify(previews=previews)


@training_bp.route('/courses/<int:course_id>/jobs', methods=['POST'])
@tenant_required
def create_training_job(course_id):
    """Create a new fine-tuning job."""
    course = Course.query.get_or_404(course_id)
    if course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    data = request.get_json() or {}

    if not data.get('base_model'):
        return jsonify(error='base_model is required'), 400

    # Validate training data exists
    svc = _get_training_service()
    stats = svc.get_training_stats(course_id)
    if stats['total_edited'] == 0:
        return jsonify(error='No edited submissions available for training. Review and edit some submissions first.'), 400

    job = TrainingJob(
        course_id=course_id,
        created_by_id=g.current_user.id,
        base_model=data['base_model'],
        training_config={
            'epochs': data.get('epochs', 3),
            'learning_rate': data.get('learning_rate', 2e-5),
            'lora_rank': data.get('lora_rank', 16),
            'batch_size': data.get('batch_size', 4),
            'warmup_ratio': data.get('warmup_ratio', 0.1),
        },
        training_samples=stats['total_edited'],
    )
    db.session.add(job)
    db.session.commit()

    # Launch async Celery task
    from app.tasks.training_tasks import run_finetuning_task
    run_finetuning_task.delay(job.id, course_id)

    return jsonify(job=job.to_dict()), 201


@training_bp.route('/jobs/<int:job_id>', methods=['GET'])
@tenant_required
def get_training_job(job_id):
    """Get training job status."""
    job = TrainingJob.query.get_or_404(job_id)
    if job.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404
    return jsonify(job=job.to_dict())


@training_bp.route('/courses/<int:course_id>/jobs', methods=['GET'])
@tenant_required
def list_training_jobs(course_id):
    """List all training jobs for a course."""
    course = Course.query.get_or_404(course_id)
    if course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    jobs = TrainingJob.query.filter_by(course_id=course_id).order_by(
        TrainingJob.created_at.desc()
    ).all()

    return jsonify(jobs=[j.to_dict() for j in jobs])


@training_bp.route('/jobs/<int:job_id>/cancel', methods=['POST'])
@tenant_required
def cancel_training_job(job_id):
    """Cancel a running training job."""
    job = TrainingJob.query.get_or_404(job_id)
    if job.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    if job.status not in ('pending', 'preparing', 'training'):
        return jsonify(error='Job cannot be cancelled in current state'), 400

    job.status = 'failed'
    job.error_message = 'Cancelled by user'
    db.session.commit()

    return jsonify(job=job.to_dict())
