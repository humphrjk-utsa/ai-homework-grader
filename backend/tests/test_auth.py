"""Tests for auth endpoints."""
import pytest


class TestRegister:
    def test_register_creates_org_and_admin(self, client):
        resp = client.post('/api/auth/register', json={
            'email': 'admin@school.edu',
            'password': 'pass1234',
            'first_name': 'Admin',
            'last_name': 'User',
            'organization_name': 'State U',
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['user']['role'] == 'admin'
        assert data['user']['email'] == 'admin@school.edu'
        assert 'access_token' in data
        assert 'refresh_token' in data

    def test_second_user_same_org_is_instructor(self, client):
        # First user = admin
        client.post('/api/auth/register', json={
            'email': 'first@school.edu',
            'password': 'pass1234',
            'first_name': 'First',
            'last_name': 'User',
            'organization_name': 'Same Org',
        })
        # Second user = instructor
        resp = client.post('/api/auth/register', json={
            'email': 'second@school.edu',
            'password': 'pass1234',
            'first_name': 'Second',
            'last_name': 'User',
            'organization_name': 'Same Org',
        })
        assert resp.status_code == 201
        assert resp.get_json()['user']['role'] == 'instructor'

    def test_duplicate_email_rejected(self, client):
        client.post('/api/auth/register', json={
            'email': 'dup@school.edu',
            'password': 'pass1234',
            'first_name': 'A',
            'last_name': 'B',
            'organization_name': 'Org',
        })
        resp = client.post('/api/auth/register', json={
            'email': 'dup@school.edu',
            'password': 'pass1234',
            'first_name': 'C',
            'last_name': 'D',
            'organization_name': 'Org',
        })
        assert resp.status_code == 409

    def test_missing_field_returns_400(self, client):
        resp = client.post('/api/auth/register', json={
            'email': 'x@school.edu',
            'password': 'pass1234',
        })
        assert resp.status_code == 400


class TestLogin:
    def test_login_success(self, client):
        client.post('/api/auth/register', json={
            'email': 'login@school.edu',
            'password': 'pass1234',
            'first_name': 'L',
            'last_name': 'U',
            'organization_name': 'Org',
        })
        resp = client.post('/api/auth/login', json={
            'email': 'login@school.edu',
            'password': 'pass1234',
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data

    def test_login_wrong_password(self, client):
        client.post('/api/auth/register', json={
            'email': 'wrong@school.edu',
            'password': 'pass1234',
            'first_name': 'W',
            'last_name': 'U',
            'organization_name': 'Org',
        })
        resp = client.post('/api/auth/login', json={
            'email': 'wrong@school.edu',
            'password': 'badpass',
        })
        assert resp.status_code == 401


class TestProfile:
    def test_get_profile(self, client, auth_headers):
        resp = client.get('/api/auth/me', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['user']['email'] == 'test@example.com'

    def test_update_profile(self, client, auth_headers):
        resp = client.put('/api/auth/me', headers=auth_headers, json={
            'first_name': 'Updated',
        })
        assert resp.status_code == 200
        assert resp.get_json()['user']['first_name'] == 'Updated'

    def test_profile_requires_auth(self, client):
        resp = client.get('/api/auth/me')
        assert resp.status_code == 401


class TestRefresh:
    def test_refresh_token(self, client):
        resp = client.post('/api/auth/register', json={
            'email': 'refresh@school.edu',
            'password': 'pass1234',
            'first_name': 'R',
            'last_name': 'U',
            'organization_name': 'Org',
        })
        refresh_token = resp.get_json()['refresh_token']
        resp = client.post('/api/auth/refresh', headers={
            'Authorization': f'Bearer {refresh_token}',
        })
        assert resp.status_code == 200
        assert 'access_token' in resp.get_json()
