"""Health check and dashboard endpoints."""
import os
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, g, current_app

from app.utils.decorators import tenant_required

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check - no auth required."""
    return jsonify(status='ok', service='ai-homework-grader-api')


@health_bp.route('/health/models', methods=['GET'])
def model_status():
    """Check AI model backend availability."""
    status = {
        'vllm': {'available': False},
        'parallax': {'available': False},
        'ollama': {'available': False},
    }

    # Check vLLM
    try:
        from engine.models.vllm_client import VLLMClient
        config_path = current_app.config.get('CLUSTER_CONFIG_PATH')
        if config_path and os.path.exists(config_path):
            import json
            with open(config_path) as f:
                config = json.load(f)
            vllm_config = config.get('vllm', {})
            if vllm_config.get('enabled'):
                client = VLLMClient(
                    qwen_server_url=vllm_config.get('qwen_server_url'),
                    gptoss_server_url=vllm_config.get('gptoss_server_url'),
                )
                sys_status = client.get_system_status()
                status['vllm'] = {
                    'available': sys_status.get('distributed_ready', False),
                    'qwen_online': sys_status.get('qwen_online', False),
                    'gptoss_online': sys_status.get('gptoss_online', False),
                }
    except Exception as e:
        status['vllm']['error'] = str(e)

    # Check Ollama
    try:
        import requests
        resp = requests.get('http://localhost:11434/api/tags', timeout=3)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            status['ollama'] = {
                'available': True,
                'models': [m.get('name') for m in models[:5]],
            }
    except Exception:
        pass

    return jsonify(status)


@health_bp.route('/dashboard', methods=['GET'])
@tenant_required
def dashboard():
    """Dashboard data: recent jobs, pending reviews, upcoming deadlines."""
    from app.models.grading_job import GradingJob
    from app.models.submission import Submission
    from app.models.assignment import Assignment
    from app.models.course import Course

    # Recent grading jobs for current user
    recent_jobs = GradingJob.query.filter_by(
        created_by_id=g.current_user.id
    ).order_by(GradingJob.created_at.desc()).limit(10).all()

    # Pending review count (graded but not reviewed in user's org)
    pending_review_count = Submission.query.join(Assignment).join(Course).filter(
        Course.organization_id == g.organization_id,
        Submission.status == 'graded',
    ).count()

    # Upcoming deadlines (assignments with due_date in next 14 days)
    now = datetime.utcnow()
    two_weeks = now + timedelta(days=14)
    upcoming = Assignment.query.join(Course).filter(
        Course.organization_id == g.organization_id,
        Assignment.due_date.isnot(None),
        Assignment.due_date >= now,
        Assignment.due_date <= two_weeks,
    ).order_by(Assignment.due_date.asc()).limit(10).all()

    return jsonify(
        recent_jobs=[j.to_dict() for j in recent_jobs],
        pending_review_count=pending_review_count,
        upcoming_deadlines=[{
            'id': a.id,
            'name': a.name,
            'course_id': a.course_id,
            'due_date': a.due_date.isoformat() if a.due_date else None,
            'total_submissions': a.submissions.count(),
        } for a in upcoming],
    )
