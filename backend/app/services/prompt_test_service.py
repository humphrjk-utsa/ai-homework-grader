"""
PromptTestService: Run prompt tests against real submissions without
writing results to submission records. Used by the Prompt Playground.
"""
import time
import logging
from datetime import datetime

from app.extensions import db
from app.models.prompt_test_run import PromptTestRun

logger = logging.getLogger(__name__)


class PromptTestService:
    def __init__(self, storage_root: str):
        self.storage_root = storage_root

    def _grade_one(self, submission, prompts: dict, capture: bool = True) -> dict:
        """Grade a single submission with the given prompt overrides."""
        from app.services.grading_service import GradingService
        service = GradingService(self.storage_root)
        return service.grade_submission(
            submission,
            capture_prompts=capture,
            custom_prompt_overrides=prompts,
        )

    def run_test(self, test_run: PromptTestRun):
        """Execute a prompt test run (any type). Updates the DB record in place."""
        from app.models.submission import Submission

        test_run.status = 'running'
        db.session.commit()

        start = time.time()

        try:
            submissions = Submission.query.filter(
                Submission.id.in_(test_run.submission_ids or [])
            ).all()

            if not submissions:
                raise ValueError('No valid submissions found for test')

            prompts_a = {
                'code_analysis': test_run.code_analysis_prompt,
                'feedback': test_run.feedback_prompt,
            }

            if test_run.run_type == 'comparison':
                prompts_b = {
                    'code_analysis': test_run.comparison_code_analysis_prompt,
                    'feedback': test_run.comparison_feedback_prompt,
                }
                results = self._run_comparison(submissions, prompts_a, prompts_b)
            else:
                results = self._run_standard(submissions, prompts_a)

            test_run.results = results
            test_run.status = 'completed'
            test_run.total_duration_seconds = round(time.time() - start, 2)
            test_run.grading_stats = self._compute_stats(results, test_run.run_type)
            test_run.completed_at = datetime.utcnow()

        except Exception as e:
            logger.exception(f'Prompt test run {test_run.id} failed')
            test_run.status = 'error'
            test_run.error_message = str(e)
            test_run.total_duration_seconds = round(time.time() - start, 2)

        db.session.commit()

    def _run_standard(self, submissions, prompts: dict) -> dict:
        """Run prompts against one or more submissions."""
        results = {}
        for sub in submissions:
            student = sub.student
            name = f"{student.first_name} {student.last_name}" if student else "Unknown"
            try:
                result = self._grade_one(sub, prompts)
                results[str(sub.id)] = {
                    'student_name': name,
                    'score': result.get('final_score'),
                    'max_points': result.get('max_points'),
                    'feedback': result,
                    'raw_prompts': result.get('raw_prompts'),
                    'grading_stats': result.get('grading_stats'),
                    'error': None,
                }
            except Exception as e:
                results[str(sub.id)] = {
                    'student_name': name,
                    'score': None,
                    'error': str(e),
                }
        return results

    def _run_comparison(self, submissions, prompts_a: dict, prompts_b: dict) -> dict:
        """Run two prompt versions against the same submissions."""
        results = {'version_a': {}, 'version_b': {}}
        for sub in submissions:
            student = sub.student
            name = f"{student.first_name} {student.last_name}" if student else "Unknown"

            # Version A
            try:
                result_a = self._grade_one(sub, prompts_a)
                results['version_a'][str(sub.id)] = {
                    'student_name': name,
                    'score': result_a.get('final_score'),
                    'max_points': result_a.get('max_points'),
                    'feedback': result_a,
                    'raw_prompts': result_a.get('raw_prompts'),
                    'error': None,
                }
            except Exception as e:
                results['version_a'][str(sub.id)] = {
                    'student_name': name,
                    'score': None,
                    'error': str(e),
                }

            # Version B
            try:
                result_b = self._grade_one(sub, prompts_b)
                results['version_b'][str(sub.id)] = {
                    'student_name': name,
                    'score': result_b.get('final_score'),
                    'max_points': result_b.get('max_points'),
                    'feedback': result_b,
                    'raw_prompts': result_b.get('raw_prompts'),
                    'error': None,
                }
            except Exception as e:
                results['version_b'][str(sub.id)] = {
                    'student_name': name,
                    'score': None,
                    'error': str(e),
                }

        return results

    def _compute_stats(self, results: dict, run_type: str) -> dict:
        """Compute summary statistics from results."""
        def _stats_from_entries(entries: dict) -> dict:
            scores = [v['score'] for v in entries.values() if v.get('score') is not None]
            return {
                'total': len(entries),
                'successful': len(scores),
                'failed': len(entries) - len(scores),
                'avg_score': round(sum(scores) / len(scores), 2) if scores else None,
                'min_score': min(scores) if scores else None,
                'max_score': max(scores) if scores else None,
            }

        if run_type == 'comparison':
            return {
                'version_a': _stats_from_entries(results.get('version_a', {})),
                'version_b': _stats_from_entries(results.get('version_b', {})),
            }
        return _stats_from_entries(results)
