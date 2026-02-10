"""Celery tasks for async report generation."""
import logging

from app.tasks.celery_app import celery_app
from app.extensions import db

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name='reports.generate_report')
def generate_report_task(self, submission_id, generated_by_id):
    """Generate a PDF report for a single submission."""
    from app.models.submission import Submission
    from app.services.report_service import ReportService
    from flask import current_app

    sub = db.session.get(Submission, submission_id)
    if not sub:
        logger.error(f'Submission {submission_id} not found')
        return

    service = ReportService(current_app.config['STORAGE_ROOT'])
    report = service.generate_report(sub, generated_by_id)
    return {'report_id': report.id, 'file_path': report.file_path}
