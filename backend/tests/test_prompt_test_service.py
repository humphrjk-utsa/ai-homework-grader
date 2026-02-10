"""Tests for PromptTestService: stats computation, standard/comparison modes."""
import pytest

from app.services.prompt_test_service import PromptTestService


class TestComputeStats:
    """Test _compute_stats with synthetic result data (no DB needed)."""

    def setup_method(self):
        self.service = PromptTestService.__new__(PromptTestService)
        self.service.storage_root = '/tmp'

    def test_standard_stats(self):
        results = {
            '1': {'student_name': 'Alice', 'score': 80, 'error': None},
            '2': {'student_name': 'Bob', 'score': 90, 'error': None},
            '3': {'student_name': 'Charlie', 'score': 70, 'error': None},
        }
        stats = self.service._compute_stats(results, 'single')
        assert stats['total'] == 3
        assert stats['successful'] == 3
        assert stats['failed'] == 0
        assert stats['avg_score'] == 80.0
        assert stats['min_score'] == 70
        assert stats['max_score'] == 90

    def test_standard_stats_with_failures(self):
        results = {
            '1': {'student_name': 'Alice', 'score': 80, 'error': None},
            '2': {'student_name': 'Bob', 'score': None, 'error': 'File not found'},
        }
        stats = self.service._compute_stats(results, 'sample')
        assert stats['total'] == 2
        assert stats['successful'] == 1
        assert stats['failed'] == 1
        assert stats['avg_score'] == 80.0

    def test_standard_stats_all_failed(self):
        results = {
            '1': {'student_name': 'Alice', 'score': None, 'error': 'Error'},
        }
        stats = self.service._compute_stats(results, 'single')
        assert stats['total'] == 1
        assert stats['successful'] == 0
        assert stats['avg_score'] is None

    def test_comparison_stats(self):
        results = {
            'version_a': {
                '1': {'student_name': 'Alice', 'score': 85, 'error': None},
                '2': {'student_name': 'Bob', 'score': 75, 'error': None},
            },
            'version_b': {
                '1': {'student_name': 'Alice', 'score': 90, 'error': None},
                '2': {'student_name': 'Bob', 'score': 80, 'error': None},
            },
        }
        stats = self.service._compute_stats(results, 'comparison')
        assert 'version_a' in stats
        assert 'version_b' in stats
        assert stats['version_a']['avg_score'] == 80.0
        assert stats['version_b']['avg_score'] == 85.0
        assert stats['version_a']['successful'] == 2
        assert stats['version_b']['successful'] == 2

    def test_empty_results(self):
        stats = self.service._compute_stats({}, 'single')
        assert stats['total'] == 0
        assert stats['successful'] == 0
        assert stats['avg_score'] is None

    def test_comparison_empty_versions(self):
        results = {'version_a': {}, 'version_b': {}}
        stats = self.service._compute_stats(results, 'comparison')
        assert stats['version_a']['total'] == 0
        assert stats['version_b']['total'] == 0
