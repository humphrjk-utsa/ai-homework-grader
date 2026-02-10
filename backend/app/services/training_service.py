"""
TrainingService: Export training data from reviewed submissions,
track training statistics, and manage fine-tuning jobs.
"""
import os
import json
import logging
from datetime import datetime

from app.extensions import db

logger = logging.getLogger(__name__)


class TrainingService:
    def __init__(self, storage_root: str):
        self.storage_root = storage_root

    def get_training_stats(self, course_id: int) -> dict:
        """Get counts of reviewed/edited submissions available for training."""
        from app.models.submission import Submission
        from app.models.assignment import Assignment

        assignments = Assignment.query.filter_by(course_id=course_id).all()

        stats = {
            'total_graded': 0,
            'total_reviewed': 0,
            'total_edited': 0,
            'assignments': [],
        }

        for a in assignments:
            graded = Submission.query.filter(
                Submission.assignment_id == a.id,
                Submission.status.in_(['graded', 'reviewed']),
            ).count()

            reviewed = Submission.query.filter(
                Submission.assignment_id == a.id,
                Submission.status == 'reviewed',
            ).count()

            edited = Submission.query.filter(
                Submission.assignment_id == a.id,
                Submission.edited_feedback.isnot(None),
            ).count()

            stats['total_graded'] += graded
            stats['total_reviewed'] += reviewed
            stats['total_edited'] += edited
            stats['assignments'].append({
                'id': a.id,
                'name': a.name,
                'graded': graded,
                'reviewed': reviewed,
                'edited': edited,
            })

        return stats

    def export_training_data(self, course_id: int) -> dict:
        """Export reviewed submissions as JSONL for fine-tuning.

        Each line: {messages: [{role: "system", ...}, {role: "user", content: "<rubric+code>"},
                              {role: "assistant", content: "<edited_feedback JSON>"}]}

        Returns:
            dict with file_path and num_samples
        """
        from app.models.submission import Submission
        from app.models.assignment import Assignment

        assignments = Assignment.query.filter_by(course_id=course_id).all()

        samples = []
        for assignment in assignments:
            # Load rubric for context
            rubric_text = ''
            if assignment.rubric_path:
                course = assignment.course
                org_slug = course.organization.slug
                rubric_abs = os.path.join(
                    self.storage_root, org_slug, course.slug,
                    'assignments', assignment.slug, assignment.rubric_path,
                )
                if os.path.exists(rubric_abs):
                    try:
                        with open(rubric_abs) as f:
                            rubric_data = json.load(f)
                        rubric_text = json.dumps(rubric_data, indent=2)
                    except Exception:
                        pass

            # Get submissions with edited feedback (professor corrections)
            submissions = Submission.query.filter(
                Submission.assignment_id == assignment.id,
                Submission.edited_feedback.isnot(None),
            ).all()

            for sub in submissions:
                feedback = sub.edited_feedback
                if not feedback:
                    continue

                # Build the user prompt (what the model would see during grading)
                student_code = ''
                if sub.file_path:
                    course = assignment.course
                    org_slug = course.organization.slug
                    sub_abs = os.path.join(
                        self.storage_root, org_slug, course.slug,
                        'submissions', assignment.slug, sub.file_path,
                    )
                    if os.path.exists(sub_abs):
                        try:
                            import nbformat
                            with open(sub_abs) as f:
                                nb = nbformat.read(f, as_version=4)
                            code_cells = [c.source for c in nb.cells if c.cell_type == 'code']
                            student_code = '\n\n'.join(code_cells)[:4000]
                        except Exception:
                            pass

                user_content = f"Assignment: {assignment.name}\n"
                if rubric_text:
                    user_content += f"\nRubric:\n{rubric_text[:2000]}\n"
                user_content += f"\nStudent Code:\n{student_code}\n"
                user_content += f"\nGrade this submission and provide structured feedback."

                sample = {
                    'messages': [
                        {
                            'role': 'system',
                            'content': (
                                'You are an expert grading assistant. Analyze student submissions '
                                'and provide structured feedback in JSON format with technical_analysis, '
                                'comprehensive_feedback, and scoring.'
                            ),
                        },
                        {'role': 'user', 'content': user_content},
                        {'role': 'assistant', 'content': json.dumps(feedback)},
                    ],
                }
                samples.append(sample)

        if not samples:
            return {'file_path': None, 'num_samples': 0}

        # Write JSONL
        course = Assignment.query.filter_by(course_id=course_id).first().course
        org_slug = course.organization.slug
        export_dir = os.path.join(
            self.storage_root, org_slug, course.slug, 'training',
        )
        os.makedirs(export_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'training_data_{timestamp}.jsonl'
        file_path = os.path.join(export_dir, filename)

        with open(file_path, 'w') as f:
            for sample in samples:
                f.write(json.dumps(sample) + '\n')

        return {
            'file_path': file_path,
            'relative_path': os.path.join(org_slug, course.slug, 'training', filename),
            'num_samples': len(samples),
        }

    def get_sample_preview(self, course_id: int, limit: int = 3) -> list:
        """Return a few training data samples for preview."""
        from app.models.submission import Submission
        from app.models.assignment import Assignment

        submissions = (
            Submission.query
            .join(Assignment)
            .filter(
                Assignment.course_id == course_id,
                Submission.edited_feedback.isnot(None),
            )
            .limit(limit)
            .all()
        )

        previews = []
        for sub in submissions:
            student = sub.student
            name = f"{student.first_name} {student.last_name}" if student else "Unknown"
            feedback = sub.edited_feedback or {}

            previews.append({
                'student_name': name,
                'assignment': sub.assignment.name,
                'score': sub.final_score,
                'max_score': sub.max_score,
                'feedback_keys': list(feedback.keys()),
            })

        return previews
