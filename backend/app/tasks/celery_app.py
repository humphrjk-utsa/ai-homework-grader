"""Celery application factory and configuration."""
import os

from celery import Celery, Task

celery_app = Celery('ai_homework_grader')


class FlaskTask(Task):
    """Custom Celery task class that runs inside a Flask app context."""

    _flask_app = None

    @property
    def flask_app(self):
        if self._flask_app is None:
            from app import create_app
            config_name = os.environ.get('FLASK_CONFIG', 'development')
            self._flask_app = create_app(config_name)
        return self._flask_app

    def __call__(self, *args, **kwargs):
        with self.flask_app.app_context():
            return self.run(*args, **kwargs)


def init_celery(app):
    """Configure Celery from Flask app config and bind app context."""
    celery_app.config_from_object({
        'broker_url': app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        'result_backend': app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        'task_serializer': 'json',
        'result_serializer': 'json',
        'accept_content': ['json'],
        'task_acks_late': True,
        'worker_prefetch_multiplier': 1,
        'task_time_limit': 900,
        'task_soft_time_limit': 840,
    })

    celery_app.Task = FlaskTask
    FlaskTask._flask_app = app

    celery_app.autodiscover_tasks(['app.tasks'])

    return celery_app
