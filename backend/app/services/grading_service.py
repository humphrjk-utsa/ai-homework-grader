"""
GradingService: Wraps the existing BusinessAnalyticsGraderV2 for Flask API use.

Resolves file paths from database records to storage paths, instantiates
the grader with the correct rubric/solution, executes grading, and returns
structured results.
"""
import os
import json
import logging

logger = logging.getLogger(__name__)


class GradingService:
    def __init__(self, storage_root: str):
        self.storage_root = storage_root

    def _resolve_assignment_paths(self, submission):
        """Build absolute file paths from the submission's assignment config."""
        assignment = submission.assignment
        course = assignment.course
        org_slug = course.organization.slug

        base = os.path.join(self.storage_root, org_slug, course.slug,
                            'assignments', assignment.slug)

        paths = {
            'rubric': os.path.join(base, assignment.rubric_path) if assignment.rubric_path else None,
            'solution': os.path.join(base, assignment.solution_path) if assignment.solution_path else None,
            'template': os.path.join(base, assignment.template_path) if assignment.template_path else None,
        }

        # Submission file path
        sub_base = os.path.join(self.storage_root, org_slug, course.slug,
                                'submissions', assignment.slug)
        paths['submission'] = os.path.join(sub_base, submission.file_path)

        # Data folder (for notebook execution)
        paths['data_folder'] = os.path.join(base, 'data')

        return paths

    def grade_submission(self, submission) -> dict:
        """Grade a single submission using the engine pipeline.

        Args:
            submission: Submission ORM object with related assignment/student

        Returns:
            Structured grading result dict (same format as BusinessAnalyticsGraderV2)
        """
        assignment = submission.assignment
        paths = self._resolve_assignment_paths(submission)

        # Validate required files exist
        if not paths['rubric'] or not os.path.exists(paths['rubric']):
            raise FileNotFoundError(f"Rubric not found: {paths['rubric']}")
        if not os.path.exists(paths['submission']):
            raise FileNotFoundError(f"Submission file not found: {paths['submission']}")

        # Step 1: Execute notebook if needed
        from engine.notebook_executor import NotebookExecutor
        executor = NotebookExecutor(
            data_folder=paths['data_folder'] if os.path.exists(paths.get('data_folder', '')) else None,
            timeout=30
        )
        notebook_path = paths['submission']
        try:
            executed_path, exec_info = executor.execute_if_needed(notebook_path)
            if executed_path:
                notebook_path = executed_path
        except Exception as e:
            logger.warning(f"Notebook execution failed: {e}")
            exec_info = {'error': str(e)}

        # Step 2: Preprocess submission
        from engine.submission_preprocessor import SubmissionPreprocessor
        preprocessor = SubmissionPreprocessor()
        student_code, student_markdown, fixes = preprocessor.preprocess_notebook(notebook_path)

        # Step 3: Load template and solution
        template_code = ''
        if paths['template'] and os.path.exists(paths['template']):
            template_code = self._extract_code(paths['template'])

        solution_code = ''
        if paths['solution'] and os.path.exists(paths['solution']):
            solution_code = self._extract_code(paths['solution'])

        # Step 4: Initialize grader
        from engine.business_analytics_grader_v2 import BusinessAnalyticsGraderV2
        grader = BusinessAnalyticsGraderV2(
            rubric_path=paths['rubric'],
            solution_path=paths['solution'],
        )

        # Step 5: Build assignment info
        student = submission.student
        student_name = f"{student.first_name} {student.last_name}" if student else "Unknown"

        with open(paths['rubric']) as f:
            rubric_data = json.load(f)

        assignment_info = {
            'title': assignment.name,
            'name': assignment.name,
            'description': assignment.description or '',
            'student_name': student_name,
            'rubric': json.dumps(rubric_data),
        }

        # Step 6: Build custom prompts from DB-stored assignment prompts
        custom_prompts = {}
        if assignment.code_analysis_prompt:
            custom_prompts['code_analysis'] = assignment.code_analysis_prompt
        if assignment.feedback_prompt:
            custom_prompts['feedback'] = assignment.feedback_prompt

        # Step 7: Grade
        result = grader.grade_submission(
            student_code=student_code,
            student_markdown=student_markdown,
            template_code=template_code,
            solution_code=solution_code,
            assignment_info=assignment_info,
            notebook_path=notebook_path,
            preprocessing_info={
                'fixes_applied': fixes,
            },
            custom_prompts=custom_prompts or None,
        )

        # Step 8: Validate
        try:
            from engine.grading_validator import GradingValidator
            validator = GradingValidator(max_points=assignment.total_points)
            is_valid, errors = validator.validate_grading_result(result)
            if not is_valid:
                result = validator.fix_calculation_errors(result)
        except Exception as e:
            logger.warning(f"Grading validation failed: {e}")

        return result

    def _extract_code(self, notebook_path: str) -> str:
        """Extract code from a Jupyter notebook."""
        try:
            import nbformat
            with open(notebook_path) as f:
                nb = nbformat.read(f, as_version=4)
            code_cells = [cell.source for cell in nb.cells if cell.cell_type == 'code']
            return '\n\n'.join(code_cells)
        except Exception:
            return ''
