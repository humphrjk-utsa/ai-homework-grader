"""Tests for prefix caching: prompt_manager prefix optimization, normalization, template loading."""
import os
import sys

import pytest

# Add project root to path so engine package is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture(autouse=True)
def _run_from_project_root(monkeypatch):
    """PromptManager uses relative Path('prompt_templates'), so CWD must be project root."""
    monkeypatch.chdir(PROJECT_ROOT)


class TestNormalizePrefix:
    """Test PromptManager._normalize_prefix static method."""

    def test_strips_trailing_whitespace(self):
        from engine.prompt_manager import PromptManager
        text = "line one   \nline two\t\nline three  "
        result = PromptManager._normalize_prefix(text)
        lines = result.split('\n')
        for line in lines:
            assert line == line.rstrip()

    def test_collapses_multiple_blank_lines(self):
        from engine.prompt_manager import PromptManager
        text = "line one\n\n\n\n\nline two"
        result = PromptManager._normalize_prefix(text)
        assert '\n\n\n' not in result
        assert 'line one\n\nline two' == result

    def test_strips_leading_trailing(self):
        from engine.prompt_manager import PromptManager
        text = "\n\n  Hello World  \n\n"
        result = PromptManager._normalize_prefix(text)
        assert result == 'Hello World'

    def test_idempotent(self):
        from engine.prompt_manager import PromptManager
        text = "A\n\n\n\nB\n  \nC  "
        first = PromptManager._normalize_prefix(text)
        second = PromptManager._normalize_prefix(first)
        assert first == second


class TestLoadPrefixTemplate:
    """Test that prefix templates load from the prompt_templates directory."""

    def test_all_prefix_templates_exist(self):
        template_dir = os.path.join(PROJECT_ROOT, 'prompt_templates')
        expected = [
            'prefix_code_analysis_system.txt',
            'prefix_code_analysis_assignment.txt',
            'prefix_code_analysis_student.txt',
            'prefix_feedback_system.txt',
            'prefix_feedback_assignment.txt',
            'prefix_feedback_student.txt',
        ]
        for fname in expected:
            path = os.path.join(template_dir, fname)
            assert os.path.exists(path), f'Missing template: {fname}'

    def test_system_templates_have_no_variables(self):
        """System templates should be constant (no {var} placeholders)."""
        template_dir = os.path.join(PROJECT_ROOT, 'prompt_templates')
        import re
        for fname in ['prefix_code_analysis_system.txt', 'prefix_feedback_system.txt']:
            with open(os.path.join(template_dir, fname)) as f:
                content = f.read()
            cleaned = content.replace('{{', '').replace('}}', '')
            matches = re.findall(r'\{[a-z_]+\}', cleaned)
            assert len(matches) == 0, f'{fname} contains variables: {matches}'

    def test_student_templates_have_variables(self):
        """Student templates should have format placeholders."""
        template_dir = os.path.join(PROJECT_ROOT, 'prompt_templates')
        import re
        for fname in ['prefix_code_analysis_student.txt', 'prefix_feedback_student.txt']:
            with open(os.path.join(template_dir, fname)) as f:
                content = f.read()
            matches = re.findall(r'\{[a-z_]+\}', content)
            assert len(matches) > 0, f'{fname} has no variables'

    def test_load_prefix_template_method(self):
        from engine.prompt_manager import PromptManager
        pm = PromptManager()
        content = pm._load_prefix_template('prefix_code_analysis_system')
        assert len(content) > 100, 'System template seems too short'

    def test_load_missing_template_returns_empty(self):
        from engine.prompt_manager import PromptManager
        pm = PromptManager()
        content = pm._load_prefix_template('nonexistent_template_xyz')
        assert content == ''


class TestGetPrefixOptimizedPrompt:
    """Test the 3-layer prompt splitting."""

    def test_returns_three_keys(self):
        from engine.prompt_manager import PromptManager
        pm = PromptManager()
        result = pm.get_prefix_optimized_prompt(
            'test_assignment',
            'code_analysis',
            assignment_title='Test HW',
            rubric_criteria='Points: 100',
            template_code='# template',
            solution_code='# solution',
            student_code='x <- 1',
            validation_context='Validated',
        )
        assert 'system' in result
        assert 'assignment' in result
        assert 'student' in result

    def test_system_is_constant_across_students(self):
        """System message should be identical regardless of student data."""
        from engine.prompt_manager import PromptManager
        pm = PromptManager()

        common = dict(
            assignment_title='Test HW',
            rubric_criteria='Points: 100',
            template_code='# template',
            solution_code='# solution',
            validation_context='OK',
        )

        r1 = pm.get_prefix_optimized_prompt(
            'test_assignment', 'code_analysis',
            student_code='x <- 1', **common,
        )
        r2 = pm.get_prefix_optimized_prompt(
            'test_assignment', 'code_analysis',
            student_code='y <- 2; z <- 3', **common,
        )

        assert r1['system'] == r2['system'], 'System prefix should be identical'

    def test_assignment_is_constant_across_students(self):
        """Assignment message should be identical regardless of student data."""
        from engine.prompt_manager import PromptManager
        pm = PromptManager()

        common = dict(
            assignment_title='Test HW',
            rubric_criteria='Points: 100',
            template_code='# template',
            solution_code='# solution',
            validation_context='OK',
        )

        r1 = pm.get_prefix_optimized_prompt(
            'test_assignment', 'code_analysis',
            student_code='student_a_code', **common,
        )
        r2 = pm.get_prefix_optimized_prompt(
            'test_assignment', 'code_analysis',
            student_code='completely_different_student_code', **common,
        )

        assert r1['assignment'] == r2['assignment'], 'Assignment prefix should be identical'

    def test_student_differs_per_submission(self):
        """Student message should differ when student data differs."""
        from engine.prompt_manager import PromptManager
        pm = PromptManager()

        common = dict(
            assignment_title='Test HW',
            rubric_criteria='Points: 100',
            template_code='# template',
            solution_code='# solution',
            validation_context='OK',
        )

        r1 = pm.get_prefix_optimized_prompt(
            'test_assignment', 'code_analysis',
            student_code='code_A', **common,
        )
        r2 = pm.get_prefix_optimized_prompt(
            'test_assignment', 'code_analysis',
            student_code='code_B', **common,
        )

        assert r1['student'] != r2['student'], 'Student section should differ'

    def test_feedback_prompt_type(self):
        from engine.prompt_manager import PromptManager
        pm = PromptManager()
        result = pm.get_prefix_optimized_prompt(
            'test_assignment',
            'feedback',
            assignment_title='Test HW',
            rubric_criteria='Points: 100',
            student_markdown='# Analysis\nGood results.',
            student_code_summary='x <- 1; plot(x)',
            validation_context='All passed',
            reflection_comparison='',
        )
        assert len(result['system']) > 100
        assert 'Test HW' in result['assignment']
        assert 'Good results' in result['student']
