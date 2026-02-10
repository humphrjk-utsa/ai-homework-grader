"""Tests for course CRUD endpoints."""
import pytest


class TestCourses:
    def test_create_course(self, client, auth_headers):
        resp = client.post('/api/courses', headers=auth_headers, json={
            'name': 'Business Analytics',
            'code': 'BA 501',
            'semester': 'Spring',
            'year': 2026,
        })
        assert resp.status_code == 201
        course = resp.get_json()['course']
        assert course['name'] == 'Business Analytics'
        assert course['code'] == 'BA 501'
        assert course['slug'] == 'ba-501-spring-2026'

    def test_list_courses(self, client, auth_headers):
        client.post('/api/courses', headers=auth_headers, json={
            'name': 'Course A', 'semester': 'Fall', 'year': 2025,
        })
        client.post('/api/courses', headers=auth_headers, json={
            'name': 'Course B', 'semester': 'Spring', 'year': 2026,
        })
        resp = client.get('/api/courses', headers=auth_headers)
        assert resp.status_code == 200
        courses = resp.get_json()['courses']
        assert len(courses) >= 2

    def test_get_course(self, client, auth_headers):
        resp = client.post('/api/courses', headers=auth_headers, json={
            'name': 'Get Me', 'semester': 'Fall', 'year': 2025,
        })
        course_id = resp.get_json()['course']['id']
        resp = client.get(f'/api/courses/{course_id}', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['course']['name'] == 'Get Me'

    def test_update_course(self, client, auth_headers):
        resp = client.post('/api/courses', headers=auth_headers, json={
            'name': 'Old Name', 'semester': 'Fall', 'year': 2025,
        })
        course_id = resp.get_json()['course']['id']
        resp = client.put(f'/api/courses/{course_id}', headers=auth_headers, json={
            'name': 'New Name',
        })
        assert resp.status_code == 200
        assert resp.get_json()['course']['name'] == 'New Name'

    def test_delete_course_soft_deletes(self, client, auth_headers):
        resp = client.post('/api/courses', headers=auth_headers, json={
            'name': 'Delete Me', 'semester': 'Fall', 'year': 2025,
        })
        course_id = resp.get_json()['course']['id']
        resp = client.delete(f'/api/courses/{course_id}', headers=auth_headers)
        assert resp.status_code == 200

    def test_duplicate_slug_rejected(self, client, auth_headers):
        client.post('/api/courses', headers=auth_headers, json={
            'name': 'Same', 'code': 'CS 100', 'semester': 'Fall', 'year': 2025,
        })
        resp = client.post('/api/courses', headers=auth_headers, json={
            'name': 'Same', 'code': 'CS 100', 'semester': 'Fall', 'year': 2025,
        })
        assert resp.status_code == 409

    def test_course_stats(self, client, auth_headers):
        resp = client.post('/api/courses', headers=auth_headers, json={
            'name': 'Stats Course', 'semester': 'Fall', 'year': 2025,
        })
        course_id = resp.get_json()['course']['id']
        resp = client.get(f'/api/courses/{course_id}/stats', headers=auth_headers)
        assert resp.status_code == 200
        stats = resp.get_json()
        assert stats['assignment_count'] == 0
        assert stats['student_count'] == 0

    def test_requires_auth(self, client):
        resp = client.get('/api/courses')
        assert resp.status_code == 401
