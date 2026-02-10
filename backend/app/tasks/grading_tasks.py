"""Celery tasks for async grading."""
import logging
from datetime import datetime

from app.tasks.celery_app import celery_app
from app.extensions import db

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name='grading.grade_batch')
def grade_batch_task(self, assignment_id, job_id, submission_ids):
    """Grade a batch of submissions asynchronously.

    Mirrors the logic in grading.py:_grade_batch_sync() but runs as a
    Celery task with progress updates and cancellation support.
    """
    from app.models.grading_job import GradingJob
    from app.models.submission import Submission
    from app.services.grading_service import GradingService
    from flask import current_app

    job = db.session.get(GradingJob, job_id)
    if not job:
        logger.error(f'GradingJob {job_id} not found')
        return

    service = GradingService(current_app.config['STORAGE_ROOT'])

    for sub_id in submission_ids:
        # Check for cancellation
        db.session.refresh(job)
        if job.status == 'cancelled':
            logger.info(f'Job {job_id} cancelled, stopping')
            return

        sub = db.session.get(Submission, sub_id)
        if not sub:
            job.failed_submissions += 1
            continue

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
            logger.exception(f'Failed to grade submission {sub_id}')
            sub.status = 'error'
            sub.error_message = str(e)
            job.failed_submissions += 1

        job.progress_percent = (
            (job.completed_submissions + job.failed_submissions)
            / job.total_submissions * 100
        )
        db.session.commit()

        # Update Celery task state for polling
        self.update_state(state='PROGRESS', meta={
            'completed': job.completed_submissions,
            'failed': job.failed_submissions,
            'total': job.total_submissions,
            'percent': job.progress_percent,
        })

    job.status = 'completed'
    job.completed_at = datetime.utcnow()
    db.session.commit()

    return {
        'job_id': job_id,
        'completed': job.completed_submissions,
        'failed': job.failed_submissions,
        'total': job.total_submissions,
    }
