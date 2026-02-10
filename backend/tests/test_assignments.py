"""Tests for assignment CRUD endpoints."""
import pytest


@pytest.fixture
def course_id(client, auth_headers):
    """Create a course and return its ID."""
    resp = client.post('/api/courses', headers=auth_headers, json={
        'name': 'Test Course', 'semester': 'Spring', 'year': 2026,
    })
    return resp.get_json()['course']['id']


class TestAssignments:
    def test_create_assignment(self, client, auth_headers, course_id):
        resp = client.post(f'/api/courses/{course_id}/assignments',
                           headers=auth_headers, json={
            'name': 'Homework 1',
            'assignment_type': 'coding',
            'total_points': 100,
            'language': 'R',
        })
        assert resp.status_code == 201
        a = resp.get_json()['assignment']
        assert a['name'] == 'Homework 1'
        assert a['assignment_type'] == 'coding'
        assert a['total_points'] == 100

    def test_list_assignments(self, client, auth_headers, course_id):
        client.post(f'/api/courses/{course_id}/assignments',
                    headers=auth_headers, json={
            'name': 'HW 1', 'assignment_type': 'coding', 'total_points': 50,
        })
        client.post(f'/api/courses/{course_id}/assignments',
                    headers=auth_headers, json={
            'name': 'HW 2', 'assignment_type': 'written', 'total_points': 75,
        })
        resp = client.get(f'/api/courses/{course_id}/assignments',
                          headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.get_json()['assignments']) == 2

    def test_get_assignment(self, client, auth_headers, course_id):
        resp = client.post(f'/api/courses/{course_id}/assignments',
                           headers=auth_headers, json={
            'name': 'Fetch Me', 'assignment_type': 'coding', 'total_points': 125,
        })
        aid = resp.get_json()['assignment']['id']
        resp = client.get(f'/api/assignments/{aid}', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['assignment']['name'] == 'Fetch Me'

    def test_update_assignment(self, client, auth_headers, course_id):
        resp = client.post(f'/api/courses/{course_id}/assignments',
                           headers=auth_headers, json={
            'name': 'Update Me', 'assignment_type': 'coding', 'total_points': 50,
        })
        aid = resp.get_json()['assignment']['id']
        resp = client.put(f'/api/assignments/{aid}', headers=auth_headers, json={
            'total_points': 200,
        })
        assert resp.status_code == 200
        assert resp.get_json()['assignment']['total_points'] == 200

    def test_delete_assignment(self, client, auth_headers, course_id):
        resp = client.post(f'/api/courses/{course_id}/assignments',
                           headers=auth_headers, json={
            'name': 'Delete Me', 'assignment_type': 'coding', 'total_points': 50,
        })
        aid = resp.get_json()['assignment']['id']
        resp = client.delete(f'/api/assignments/{aid}', headers=auth_headers)
        assert resp.status_code == 200
