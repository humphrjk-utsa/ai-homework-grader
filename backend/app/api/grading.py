"""Grading endpoints: single, batch, job status."""
from datetime import datetime

from flask import Blueprint, request, jsonify, g

from app.extensions import db
from app.models.submission import Submission
from app.models.assignment import Assignment
from app.models.grading_job import GradingJob
from app.utils.decorators import tenant_required, role_required

grading_bp = Blueprint('grading', __name__)


@grading_bp.route('/single/<int:submission_id>', methods=['POST'])
@tenant_required
def grade_single(submission_id):
    """Grade a single submission synchronously."""
    submission = Submission.query.get_or_404(submission_id)
    if submission.assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    if submission.status == 'grading':
        return jsonify(error='Submission is already being graded'), 409

    submission.status = 'grading'
    db.session.commit()

    try:
        from app.services.grading_service import GradingService
        from flask import current_app

        service = GradingService(current_app.config['STORAGE_ROOT'])
        result = service.grade_submission(submission)

        submission.ai_score = result.get('final_score')
        submission.ai_feedback = result
        submission.final_score = result.get('final_score')
        submission.max_score = result.get('max_points')
        submission.component_scores = result.get('component_scores')
        submission.component_percentages = result.get('component_percentages')
        submission.validation_results = result.get('validation_results')
        submission.status = 'graded'
        submission.graded_at = datetime.utcnow()
        db.session.commit()

        return jsonify(
            submission=submission.to_dict(include_feedback=True),
            grading_stats=result.get('grading_stats'),
        )

    except Exception as e:
        submission.status = 'error'
        submission.error_message = str(e)
        db.session.commit()
        return jsonify(error='Grading failed', message=str(e)), 500


@grading_bp.route('/batch/<int:assignment_id>', methods=['POST'])
@role_required('admin', 'instructor')
def grade_batch(assignment_id):
    """Start a batch grading job (async via Celery or sync fallback)."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    # Dedup: reject if a job is already running/pending for this assignment
    existing_job = GradingJob.query.filter_by(
        assignment_id=assignment.id,
    ).filter(GradingJob.status.in_(['pending', 'running'])).first()
    if existing_job:
        return jsonify(
            error='A grading job is already in progress for this assignment.',
            job=existing_job.to_dict(),
        ), 409

    # Find ungraded submissions
    ungraded = assignment.submissions.filter(
        Submission.status.in_(['uploaded', 'error'])
    ).all()

    if not ungraded:
        return jsonify(error='No ungraded submissions found'), 400

    # Create grading job
    job = GradingJob(
        assignment_id=assignment.id,
        created_by_id=g.current_user.id,
        status='pending',
        job_type='batch',
        total_submissions=len(ungraded),
    )
    db.session.add(job)
    db.session.flush()

    # Link submissions to job
    for sub in ungraded:
        sub.grading_job_id = job.id
        sub.status = 'queued'
    db.session.commit()

    # Try Celery, fall back to sync
    submission_ids = [s.id for s in ungraded]
    try:
        from app.tasks.grading_tasks import grade_batch_task
        celery_result = grade_batch_task.delay(assignment.id, job.id, submission_ids)
        job.celery_task_id = celery_result.id
        job.status = 'running'
        job.started_at = datetime.utcnow()
        db.session.commit()
        return jsonify(job=job.to_dict(), async_mode=True), 202
    except Exception:
        # Celery not available — run synchronously
        return _grade_batch_sync(job, ungraded)


def _grade_batch_sync(job, submissions):
    """Fallback: grade all submissions synchronously."""
    from app.services.grading_service import GradingService
    from flask import current_app

    job.status = 'running'
    job.started_at = datetime.utcnow()
    db.session.commit()

    service = GradingService(current_app.config['STORAGE_ROOT'])

    for sub in submissions:
        try:
            sub.status = 'grading'
            db.session.commit()

            result = service.grade_submission(sub)

            sub.ai_score = result.get('final_score')
            sub.ai_feedback = result
            sub.final_score = result.get('final_score')
            sub.max_score = result.get('max_points')
            sub.component_scores = result.get('component_scores')
            sub.validation_results = result.get('validation_results')
            sub.status = 'graded'
            sub.graded_at = datetime.utcnow()

            job.completed_submissions += 1

        except Exception as e:
            sub.status = 'error'
            sub.error_message = str(e)
            job.failed_submissions += 1

        job.progress_percent = (
            (job.completed_submissions + job.failed_submissions)
            / job.total_submissions * 100
        )
        db.session.commit()

    job.status = 'completed'
    job.completed_at = datetime.utcnow()
    db.session.commit()

    return jsonify(job=job.to_dict(), async_mode=False)


@grading_bp.route('/jobs/<int:job_id>', methods=['GET'])
@tenant_required
def get_job_status(job_id):
    """Get grading job status and progress."""
    job = GradingJob.query.get_or_404(job_id)
    if job.assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404
    return jsonify(job=job.to_dict())


@grading_bp.route('/jobs', methods=['GET'])
@tenant_required
def list_jobs():
    """List grading jobs for the current user."""
    jobs = GradingJob.query.filter_by(
        created_by_id=g.current_user.id
    ).order_by(GradingJob.created_at.desc()).limit(20).all()
    return jsonify(jobs=[j.to_dict() for j in jobs])


@grading_bp.route('/jobs/<int:job_id>/cancel', methods=['POST'])
@tenant_required
def cancel_job(job_id):
    """Cancel a running grading job."""
    job = GradingJob.query.get_or_404(job_id)
    if job.assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    if job.status not in ('pending', 'running'):
        return jsonify(error=f'Cannot cancel job with status: {job.status}'), 400

    job.status = 'cancelled'
    job.completed_at = datetime.utcnow()

    # Reset queued submissions
    for sub in job.submissions.filter(Submission.status == 'queued'):
        sub.status = 'uploaded'
        sub.grading_job_id = None

    db.session.commit()

    # Revoke Celery task if running
    if job.celery_task_id:
        try:
            from app.tasks.grading_tasks import celery_app
            celery_app.control.revoke(job.celery_task_id, terminate=True)
        except Exception:
            pass

    return jsonify(job=job.to_dict())


@grading_bp.route('/submissions/<int:submission_id>/review', methods=['PUT'])
@tenant_required
def submit_review(submission_id):
    """Submit human review (override score, add feedback)."""
    submission = Submission.query.get_or_404(submission_id)
    if submission.assignment.course.organization_id != g.organization_id:
        return jsonify(error='Not found'), 404

    data = request.get_json() or {}

    if 'human_score' in data:
        submission.human_score = float(data['human_score'])
        submission.final_score = submission.human_score
    if 'human_feedback' in data:
        submission.human_feedback = data['human_feedback']

    submission.reviewed_at = datetime.utcnow()
    submission.status = 'reviewed'
    db.session.commit()

    return jsonify(submission=submission.to_dict(include_feedback=True))
