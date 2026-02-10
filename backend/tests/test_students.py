"""Tests for student management endpoints."""
import io
import pytest


@pytest.fixture
def course_id(client, auth_headers):
    resp = client.post('/api/courses', headers=auth_headers, json={
        'name': 'Student Course', 'semester': 'Spring', 'year': 2026,
    })
    return resp.get_json()['course']['id']


class TestStudents:
    def test_add_student(self, client, auth_headers, course_id):
        resp = client.post(f'/api/courses/{course_id}/students',
                           headers=auth_headers, json={
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane@school.edu',
            'canvas_id': '99999',
        })
        assert resp.status_code == 201
        s = resp.get_json()['student']
        assert s['first_name'] == 'Jane'
        assert s['canvas_id'] == '99999'

    def test_list_students(self, client, auth_headers, course_id):
        client.post(f'/api/courses/{course_id}/students',
                    headers=auth_headers, json={
            'first_name': 'A', 'last_name': 'B', 'email': 'a@x.edu',
        })
        client.post(f'/api/courses/{course_id}/students',
                    headers=auth_headers, json={
            'first_name': 'C', 'last_name': 'D', 'email': 'c@x.edu',
        })
        resp = client.get(f'/api/courses/{course_id}/students',
                          headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.get_json()['students']) == 2

    def test_csv_import(self, client, auth_headers, course_id):
        csv_data = "first_name,last_name,email,canvas_id\nAlice,Smith,alice@x.edu,111\nBob,Jones,bob@x.edu,222\n"
        resp = client.post(
            f'/api/courses/{course_id}/students/import',
            headers=auth_headers,
            data={'file': (io.BytesIO(csv_data.encode()), 'students.csv')},
            content_type='multipart/form-data',
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['imported'] == 2


class TestHealth:
    def test_health_no_auth_required(self, client):
        resp = client.get('/api/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'ok'
