"""Celery tasks for prompt playground testing."""
import logging

from app.tasks.celery_app import celery_app
from app.extensions import db

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name='playground.run_prompt_test')
def run_prompt_test_task(self, test_run_id):
    """Run a prompt test asynchronously."""
    from app.models.prompt_test_run import PromptTestRun
    from app.services.prompt_test_service import PromptTestService
    from flask import current_app

    test_run = db.session.get(PromptTestRun, test_run_id)
    if not test_run:
        logger.error(f'PromptTestRun {test_run_id} not found')
        return

    service = PromptTestService(current_app.config['STORAGE_ROOT'])
    service.run_test(test_run)

    return {
        'test_run_id': test_run_id,
        'status': test_run.status,
        'duration': test_run.total_duration_seconds,
    }
