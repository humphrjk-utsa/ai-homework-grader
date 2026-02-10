"""SQLAlchemy models - import all for Alembic auto-detection."""
from app.models.user import Organization, User
from app.models.course import Course, CourseMembership
from app.models.assignment import Assignment
from app.models.student import Student, CourseEnrollment
from app.models.submission import Submission
from app.models.grading_job import GradingJob
from app.models.report import Report, ReportTemplate
from app.models.training import TrainingJob, CustomModel
from app.models.prompt_test_run import PromptTestRun

__all__ = [
    'Organization', 'User',
    'Course', 'CourseMembership',
    'Assignment',
    'Student', 'CourseEnrollment',
    'Submission',
    'GradingJob',
    'Report', 'ReportTemplate',
    'TrainingJob', 'CustomModel',
    'PromptTestRun',
]
