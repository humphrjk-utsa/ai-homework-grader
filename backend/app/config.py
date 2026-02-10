"""Flask application configuration."""
import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))


class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-secret-change-me')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']

    # File storage
    STORAGE_ROOT = os.environ.get('STORAGE_ROOT', os.path.join(PROJECT_ROOT, 'storage'))
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB upload limit

    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')

    # Celery
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # Engine config paths (shared with Streamlit)
    CLUSTER_CONFIG_PATH = os.environ.get(
        'CLUSTER_CONFIG_PATH',
        os.path.join(PROJECT_ROOT, 'config', 'cluster_config.json')
    )
    PROMPT_TEMPLATES_DIR = os.path.join(PROJECT_ROOT, 'prompt_templates')
    ASSIGNMENT_PROMPTS_DIR = os.path.join(PROJECT_ROOT, 'assignment_prompts')
    RUBRICS_DIR = os.path.join(PROJECT_ROOT, 'rubrics')


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://localhost/ai_homework_grader'
    )


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    @classmethod
    def init_app(cls, app):
        assert cls.SQLALCHEMY_DATABASE_URI, 'DATABASE_URL must be set in production'
        assert cls.SECRET_KEY != 'dev-secret-change-in-production', 'Set SECRET_KEY in production'


config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
