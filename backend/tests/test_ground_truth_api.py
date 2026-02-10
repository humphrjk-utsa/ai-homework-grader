"""Tests for ground truth upload API endpoints."""
import os
import csv
import io
import json

import pytest

from app import create_app
from app.extensions import db as _db
from app.models.user import Organization, User
from app.models.course import Course
from app.models.student import Student
from app.models.assignment import Assignment
from app.models.submission import Submission


@pytest.fixture
def app(tmp_path):
    """Create app with temp storage root."""
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
        'email': 'gt@test.edu',
        'password': 'testpass123',
        'first_name': 'Ground',
        'last_name': 'Truth',
        'organization_name': 'GT University',
    })
    data = resp.get_json()
    return {'Authorization': f'Bearer {data["access_token"]}'}


@pytest.fixture
def seed(client, auth_headers, db):
    """Create course, assignment, and students via API and direct DB."""
    resp = client.post('/api/courses', headers=auth_headers, json={
        'name': 'Test Course', 'semester': 'Spring', 'year': 2026,
    })
    course = resp.get_json()['course']

    resp = client.post(f'/api/courses/{course["id"]}/assignments',
                       headers=auth_headers, json={
        'name': 'HW 1', 'assignment_type': 'coding', 'total_points': 100,
    })
    assignment = resp.get_json()['assignment']

    from app.models.user import Organization
    org = Organization.query.first()

    s1 = Student(organization_id=org.id, first_name='Alice', last_name='Smith', canvas_id='C001')
    s2 = Student(organization_id=org.id, first_name='Bob', last_name='Jones', canvas_id='C002')
    _db.session.add_all([s1, s2])
    _db.session.commit()

    return {'course': course, 'assignment': assignment, 'students': [s1, s2], 'org': org}


class TestGroundTruthUpload:
    def test_upload_csv(self, client, auth_headers, seed, tmp_path):
        aid = seed['assignment']['id']
        csv_content = 'student_name,score,feedback\nAlice Smith,85,Good work\nBob Jones,72,Needs detail\n'
        data = {
            'files': (io.BytesIO(csv_content.encode()), 'scores.csv'),
        }
        resp = client.post(
            f'/api/assignments/{aid}/ground-truth/upload',
            headers=auth_headers,
            data=data,
            content_type='multipart/form-data',
        )
        assert resp.status_code == 200
        results = resp.get_json()['results']
        assert len(results) == 1
        assert results[0]['mode'] == 'batch'
        assert results[0]['total_entries'] == 2

    def test_upload_unsupported_format(self, client, auth_headers, seed):
        aid = seed['assignment']['id']
        data = {
            'files': (io.BytesIO(b'hello'), 'data.xyz'),
        }
        resp = client.post(
            f'/api/assignments/{aid}/ground-truth/upload',
            headers=auth_headers,
            data=data,
            content_type='multipart/form-data',
        )
        assert resp.status_code == 200
        results = resp.get_json()['results']
        assert results[0].get('error')

    def test_upload_no_files(self, client, auth_headers, seed):
        aid = seed['assignment']['id']
        resp = client.post(
            f'/api/assignments/{aid}/ground-truth/upload',
            headers=auth_headers,
            content_type='multipart/form-data',
        )
        assert resp.status_code == 400

    def test_upload_requires_auth(self, client, seed):
        aid = seed['assignment']['id']
        resp = client.post(f'/api/assignments/{aid}/ground-truth/upload')
        assert resp.status_code == 401


class TestCommitGroundTruth:
    def test_commit_entries(self, client, auth_headers, seed):
        aid = seed['assignment']['id']
        s1 = seed['students'][0]

        resp = client.post(
            f'/api/assignments/{aid}/ground-truth/commit',
            headers=auth_headers,
            json={
                'entries': [
                    {
                        'student_id': s1.id,
                        'score': 85.0,
                        'edited_feedback': {
                            'final_score': 85.0,
                            'comprehensive_feedback': {'instructor_comments': 'Good'},
                        },
                    },
                ],
            },
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['committed'] == 1
        assert data['skipped'] == 0

        # Verify submission was created
        sub = Submission.query.filter_by(assignment_id=aid, student_id=s1.id).first()
        assert sub is not None
        assert sub.status == 'reviewed'
        assert sub.final_score == 85.0
        assert sub.edited_feedback['final_score'] == 85.0

    def test_commit_skips_no_student_id(self, client, auth_headers, seed):
        aid = seed['assignment']['id']
        resp = client.post(
            f'/api/assignments/{aid}/ground-truth/commit',
            headers=auth_headers,
            json={'entries': [{'score': 50}]},
        )
        assert resp.status_code == 200
        assert resp.get_json()['skipped'] == 1

    def test_commit_empty_entries(self, client, auth_headers, seed):
        aid = seed['assignment']['id']
        resp = client.post(
            f'/api/assignments/{aid}/ground-truth/commit',
            headers=auth_headers,
            json={'entries': []},
        )
        assert resp.status_code == 400
