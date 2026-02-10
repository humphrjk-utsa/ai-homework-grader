"""Prompt testing playground endpoints."""
from datetime import datetime

from flask import Blueprint, request, jsonify, g, current_app

from app.extensions import db
from app.models.prompt_test_run import PromptTestRun
from app.models.submission import Submission
from app.models.assignment import Assignment
from app.utils.decorators import tenant_required, role_required

playground_bp = Blueprint('playground', __name__)


@playground_bp.route('/test', methods=['POST'])
@role_required('admin', 'instructor')
def run_test():
    """Create and run a prompt test. Async via Celery with sync fallback."""
    data = request.get_json() or {}

    assignment_id = data.get('assignment_id')
    if not assignment_id:
        return jsonify(error='assignment_id is required'), 400

    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    run_type = data.get('run_type', 'single')
    if run_type not in ('single', 'sample', 'comparison'):
        return jsonify(error='Invalid run_type'), 400

    submission_ids = data.get('submission_ids', [])
    if not submission_ids:
        return jsonify(error='At least one submission_id is required'), 400

    # Create test run record
    test_run = PromptTestRun(
        assignment_id=assignment_id,
        created_by_id=g.current_user.id,
        run_type=run_type,
        label=data.get('label'),
        code_analysis_prompt=data.get('code_analysis_prompt'),
        feedback_prompt=data.get('feedback_prompt'),
        comparison_code_analysis_prompt=data.get('comparison_code_analysis_prompt'),
        comparison_feedback_prompt=data.get('comparison_feedback_prompt'),
        submission_ids=submission_ids,
        status='pending',
    )
    db.session.add(test_run)
    db.session.commit()

    # Try Celery, fall back to sync
    try:
        from app.tasks.playground_tasks import run_prompt_test_task
        run_prompt_test_task.delay(test_run.id)
        return jsonify(test_run=test_run.to_dict(), async_mode=True), 202
    except Exception:
        # Celery not available — run synchronously
        from app.services.prompt_test_service import PromptTestService
        service = PromptTestService(current_app.config['STORAGE_ROOT'])
        service.run_test(test_run)
        return jsonify(test_run=test_run.to_dict(), async_mode=False)


@playground_bp.route('/test/<int:test_run_id>', methods=['GET'])
@tenant_required
def get_test_run(test_run_id):
    """Get a test run result (poll for completion)."""
    test_run = PromptTestRun.query.get_or_404(test_run_id)
    if test_run.assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404
    return jsonify(test_run=test_run.to_dict())


@playground_bp.route('/assignments/<int:assignment_id>/history', methods=['GET'])
@tenant_required
def get_test_history(assignment_id):
    """List test run history for an assignment."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    runs = PromptTestRun.query.filter_by(
        assignment_id=assignment_id,
    ).order_by(PromptTestRun.created_at.desc()).limit(50).all()

    return jsonify(runs=[r.to_dict() for r in runs])


@playground_bp.route('/test/<int:test_run_id>/apply', methods=['POST'])
@role_required('admin', 'instructor')
def apply_test_prompts(test_run_id):
    """Apply a test run's prompts to the assignment (with version lock)."""
    test_run = PromptTestRun.query.get_or_404(test_run_id)
    if test_run.assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    if test_run.status != 'completed':
        return jsonify(error='Can only apply prompts from completed test runs'), 400

    data = request.get_json() or {}
    version = data.get('version')  # 'a' or 'b' for comparison runs

    assignment = test_run.assignment
    expected_version = data.get('assignment_version')
    if expected_version is not None and assignment.version != expected_version:
        return jsonify(error='Assignment was modified. Refresh and try again.'), 409

    if test_run.run_type == 'comparison' and version == 'b':
        assignment.code_analysis_prompt = test_run.comparison_code_analysis_prompt
        assignment.feedback_prompt = test_run.comparison_feedback_prompt
    else:
        assignment.code_analysis_prompt = test_run.code_analysis_prompt
        assignment.feedback_prompt = test_run.feedback_prompt

    assignment.version += 1
    db.session.commit()

    return jsonify(assignment=assignment.to_dict())


@playground_bp.route('/test/<int:test_run_id>', methods=['DELETE'])
@role_required('admin', 'instructor')
def delete_test_run(test_run_id):
    """Delete a test run."""
    test_run = PromptTestRun.query.get_or_404(test_run_id)
    if test_run.assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    db.session.delete(test_run)
    db.session.commit()

    return jsonify(deleted=True)
