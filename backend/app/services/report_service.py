"""ReportService: Wraps PDFReportGenerator for Flask API use."""
import os
from datetime import datetime

from app.extensions import db
from app.models.report import Report


class ReportService:
    def __init__(self, storage_root: str):
        self.storage_root = storage_root

    def generate_report(self, submission, generated_by_id: int) -> Report:
        """Generate a PDF report for a graded submission.

        Args:
            submission: Submission ORM object (must be graded)
            generated_by_id: User ID who triggered generation

        Returns:
            Report ORM object
        """
        assignment = submission.assignment
        course = assignment.course
        student = submission.student
        org_slug = course.organization.slug

        # Build report output path
        report_dir = os.path.join(
            self.storage_root, org_slug, course.slug,
            'reports', assignment.slug
        )
        os.makedirs(report_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{student.last_name}_{student.first_name}_report_{timestamp}.pdf'
        report_path = os.path.join(report_dir, filename)

        # Build analysis_result dict for PDFReportGenerator
        # Prefer professor-edited feedback over original AI feedback
        feedback = submission.edited_feedback or submission.ai_feedback or {}
        analysis_result = {
            'total_score': submission.final_score or submission.ai_score or 0,
            'max_score': submission.max_score or assignment.total_points,
            'validation_results': submission.validation_results or {},
            'comprehensive_feedback': feedback.get('comprehensive_feedback', {}),
            'technical_analysis': feedback.get('technical_analysis', {}),
            'grading_timestamp': (
                submission.graded_at.strftime('%Y-%m-%d %H:%M:%S')
                if submission.graded_at else ''
            ),
        }

        # Generate PDF
        from engine.report_generator import PDFReportGenerator
        generator = PDFReportGenerator()
        student_name = f"{student.first_name} {student.last_name}"
        generator.generate_report(student_name, assignment.name, analysis_result, report_path)

        # Relative path for DB storage
        relative_path = os.path.join(
            org_slug, course.slug, 'reports', assignment.slug, filename
        )

        # Get file size
        file_size = os.path.getsize(report_path) if os.path.exists(report_path) else 0

        # Create report record
        report = Report(
            submission_id=submission.id,
            file_path=relative_path,
            file_size=file_size,
            generated_by_id=generated_by_id,
        )
        db.session.add(report)
        db.session.commit()

        return report
