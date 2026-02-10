"""Tests for prompt playground API endpoints."""
import os
import json
from unittest.mock import patch, MagicMock

import pytest

from app import create_app
from app.extensions import db as _db
from app.models.user import Organization, User
from app.models.course import Course
from app.models.student import Student
from app.models.assignment import Assignment
from app.models.submission import Submission
from app.models.prompt_test_run import PromptTestRun


@pytest.fixture
def app(tmp_path):
    os.environ['STORAGE_ROOT'] = str(tmp_path)
    app = create_app('testing')
    app.config['STORAGE_ROOT'] = str(tmp_path)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    return app.test_client()


@pytest.fixture
def auth_headers(client, db):
    resp = client.post('/api/auth/register', json={
        'email': 'play@test.edu',
        'password': 'testpass123',
        'first_name': 'Play',
        'last_name': 'Ground',
        'organization_name': 'Play University',
    })
    data = resp.get_json()
    return {'Authorization': f'Bearer {data["access_token"]}'}


@pytest.fixture
def seed(client, auth_headers, db):
    """Create course, assignment, student, and submission."""
    resp = client.post('/api/courses', headers=auth_headers, json={
        'name': 'Test Course', 'semester': 'Spring', 'year': 2026,
    })
    course = resp.get_json()['course']

    resp = client.post(f'/api/courses/{course["id"]}/assignments',
                       headers=auth_headers, json={
        'name': 'HW 1', 'assignment_type': 'coding', 'total_points': 100,
    })
    assignment = resp.get_json()['assignment']

    org = Organization.query.first()
    student = Student(organization_id=org.id, first_name='Test', last_name='Student')
    _db.session.add(student)
    _db.session.flush()

    sub = Submission(
        assignment_id=assignment['id'],
        student_id=student.id,
        original_filename='test.ipynb',
        file_type='ipynb',
        status='uploaded',
    )
    _db.session.add(sub)
    _db.session.commit()

    return {
        'course': course,
        'assignment': assignment,
        'student': student,
        'submission': sub,
        'org': org,
    }


class TestRunTest:
    def test_run_test_requires_auth(self, client):
        resp = client.post('/api/playground/test', json={})
        assert resp.status_code == 401

    def test_run_test_requires_assignment_id(self, client, auth_headers):
        resp = client.post('/api/playground/test', headers=auth_headers, json={})
        assert resp.status_code == 400
        assert 'assignment_id' in resp.get_json()['error']

    def test_run_test_requires_submission_ids(self, client, auth_headers, seed):
        resp = client.post('/api/playground/test', headers=auth_headers, json={
            'assignment_id': seed['assignment']['id'],
            'run_type': 'single',
        })
        assert resp.status_code == 400
        assert 'submission_id' in resp.get_json()['error']

    def test_run_test_invalid_run_type(self, client, auth_headers, seed):
        resp = client.post('/api/playground/test', headers=auth_headers, json={
            'assignment_id': seed['assignment']['id'],
            'run_type': 'invalid',
            'submission_ids': [seed['submission'].id],
        })
        assert resp.status_code == 400

    @patch('app.services.prompt_test_service.PromptTestService.run_test')
    def test_run_test_sync_fallback(self, mock_run, client, auth_headers, seed):
        """When Celery is unavailable, should run synchronously."""
        mock_run.return_value = None

        # Patch the run_test to simulate completion
        def set_completed(test_run):
            test_run.status = 'completed'
            test_run.results = {'1': {'score': 80}}
            test_run.total_duration_seconds = 1.5

        mock_run.side_effect = set_completed

        resp = client.post('/api/playground/test', headers=auth_headers, json={
            'assignment_id': seed['assignment']['id'],
            'run_type': 'single',
            'submission_ids': [seed['submission'].id],
            'code_analysis_prompt': 'Test prompt A',
            'feedback_prompt': 'Test prompt B',
            'label': 'test-v1',
        })
        # Accept both 200 (sync) and 202 (async)
        assert resp.status_code in (200, 202)
        data = resp.get_json()
        assert 'test_run' in data
        assert data['test_run']['run_type'] == 'single'
        assert data['test_run']['label'] == 'test-v1'

    def test_run_test_creates_record(self, client, auth_headers, seed):
        """Even if grading fails, the PromptTestRun record should be created."""
        with patch('app.services.prompt_test_service.PromptTestService.run_test'):
            resp = client.post('/api/playground/test', headers=auth_headers, json={
                'assignment_id': seed['assignment']['id'],
                'run_type': 'sample',
                'submission_ids': [seed['submission'].id],
            })
        assert resp.status_code in (200, 202)
        # Verify record exists in DB
        run_id = resp.get_json()['test_run']['id']
        run = PromptTestRun.query.get(run_id)
        assert run is not None
        assert run.run_type == 'sample'


class TestGetTestRun:
    def test_get_test_run(self, client, auth_headers, seed, db):
        user = User.query.first()
        run = PromptTestRun(
            assignment_id=seed['assignment']['id'],
            created_by_id=user.id,
            run_type='single',
            submission_ids=[seed['submission'].id],
            status='completed',
            results={'1': {'score': 85}},
        )
        db.session.add(run)
        db.session.commit()

        resp = client.get(f'/api/playground/test/{run.id}', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()['test_run']
        assert data['status'] == 'completed'
        assert data['results'] == {'1': {'score': 85}}

    def test_get_nonexistent_run(self, client, auth_headers):
        resp = client.get('/api/playground/test/99999', headers=auth_headers)
        assert resp.status_code == 404


class TestGetTestHistory:
    def test_list_history(self, client, auth_headers, seed, db):
        user = User.query.first()
        for i in range(3):
            run = PromptTestRun(
                assignment_id=seed['assignment']['id'],
                created_by_id=user.id,
                run_type='single',
                submission_ids=[seed['submission'].id],
                status='completed',
                label=f'run-{i}',
            )
            db.session.add(run)
        db.session.commit()

        resp = client.get(
            f'/api/playground/assignments/{seed["assignment"]["id"]}/history',
            headers=auth_headers,
        )
        assert resp.status_code == 200
        runs = resp.get_json()['runs']
        assert len(runs) == 3


class TestApplyTestPrompts:
    def test_apply_version_a(self, client, auth_headers, seed, db):
        user = User.query.first()
        run = PromptTestRun(
            assignment_id=seed['assignment']['id'],
            created_by_id=user.id,
            run_type='single',
            submission_ids=[seed['submission'].id],
            status='completed',
            code_analysis_prompt='New code prompt',
            feedback_prompt='New feedback prompt',
        )
        db.session.add(run)
        db.session.commit()

        assignment = Assignment.query.get(seed['assignment']['id'])
        current_version = assignment.version

        resp = client.post(
            f'/api/playground/test/{run.id}/apply',
            headers=auth_headers,
            json={'assignment_version': current_version},
        )
        assert resp.status_code == 200
        updated = resp.get_json()['assignment']
        assert updated['code_analysis_prompt'] == 'New code prompt'
        assert updated['feedback_prompt'] == 'New feedback prompt'
        assert updated['version'] == current_version + 1

    def test_apply_comparison_version_b(self, client, auth_headers, seed, db):
        user = User.query.first()
        run = PromptTestRun(
            assignment_id=seed['assignment']['id'],
            created_by_id=user.id,
            run_type='comparison',
            submission_ids=[seed['submission'].id],
            status='completed',
            code_analysis_prompt='A code',
            feedback_prompt='A feedback',
            comparison_code_analysis_prompt='B code',
            comparison_feedback_prompt='B feedback',
        )
        db.session.add(run)
        db.session.commit()

        assignment = Assignment.query.get(seed['assignment']['id'])
        current_version = assignment.version

        resp = client.post(
            f'/api/playground/test/{run.id}/apply',
            headers=auth_headers,
            json={'version': 'b', 'assignment_version': current_version},
        )
        assert resp.status_code == 200
        updated = resp.get_json()['assignment']
        assert updated['code_analysis_prompt'] == 'B code'
        assert updated['feedback_prompt'] == 'B feedback'

    def test_apply_version_lock_conflict(self, client, auth_headers, seed, db):
        user = User.query.first()
        run = PromptTestRun(
            assignment_id=seed['assignment']['id'],
            created_by_id=user.id,
            run_type='single',
            submission_ids=[seed['submission'].id],
            status='completed',
            code_analysis_prompt='Prompt',
            feedback_prompt='Prompt',
        )
        db.session.add(run)
        db.session.commit()

        resp = client.post(
            f'/api/playground/test/{run.id}/apply',
            headers=auth_headers,
            json={'assignment_version': 999},  # wrong version
        )
        assert resp.status_code == 409

    def test_apply_incomplete_run(self, client, auth_headers, seed, db):
        user = User.query.first()
        run = PromptTestRun(
            assignment_id=seed['assignment']['id'],
            created_by_id=user.id,
            run_type='single',
            submission_ids=[seed['submission'].id],
            status='running',
        )
        db.session.add(run)
        db.session.commit()

        resp = client.post(
            f'/api/playground/test/{run.id}/apply',
            headers=auth_headers,
            json={},
        )
        assert resp.status_code == 400


class TestDeleteTestRun:
    def test_delete_run(self, client, auth_headers, seed, db):
        user = User.query.first()
        run = PromptTestRun(
            assignment_id=seed['assignment']['id'],
            created_by_id=user.id,
            run_type='single',
            submission_ids=[seed['submission'].id],
            status='completed',
        )
        db.session.add(run)
        db.session.commit()
        run_id = run.id

        resp = client.delete(f'/api/playground/test/{run_id}', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['deleted'] is True
        assert PromptTestRun.query.get(run_id) is None

    def test_delete_nonexistent(self, client, auth_headers):
        resp = client.delete('/api/playground/test/99999', headers=auth_headers)
        assert resp.status_code == 404
