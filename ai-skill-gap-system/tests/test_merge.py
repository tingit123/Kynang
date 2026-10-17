"""Integration checks using an isolated in-memory database, never the live MySQL."""
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base, get_db
from src.main import app
from src.models.user import User
from src.core.security import create_access_token, create_refresh_token, get_password_hash


class MergeIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.admin = User(email='admin@example.com', full_name='Admin', role='admin', password_hash=get_password_hash('admin123'))
        self.candidate = User(email='candidate@example.com', full_name='Candidate', role='candidate', password_hash=get_password_hash('secret123'))
        self.session.add_all([self.admin, self.candidate])
        self.session.commit()

        def db_override():
            yield self.session

        app.dependency_overrides[get_db] = db_override
        # Do not start lifespan: it initializes MySQL and the expiry worker.
        self.client = TestClient(app)
        self.headers = self.auth(self.admin)

    def auth(self, user):
        return {'Authorization': 'Bearer ' + create_access_token({'sub': str(user.id)})}

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.session.close()
        self.engine.dispose()

    def test_account_lifecycle_persists_and_preserves_history(self):
        payload = {'email':'new@example.com', 'full_name':'New user', 'password':'secret123', 'phone':'0123456789', 'role':'employer', 'company_name':'Company'}
        response = self.client.post('/api/users/', headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 201, response.text)
        user_id = response.json()['id']
        self.assertNotIn('password_hash', response.json())
        self.assertEqual(self.client.post('/api/users/', headers=self.headers, json=payload).status_code, 409)
        response = self.client.put(f'/api/users/{user_id}', headers=self.headers, json={'full_name':'Edited', 'is_active':False})
        self.assertEqual(response.status_code, 200, response.text)
        user = self.session.get(User, user_id)
        self.assertEqual(user.full_name, 'Edited')
        self.assertEqual(user.phone, '0123456789')
        self.assertEqual(self.client.get('/api/auth/me', headers=self.auth(user)).status_code, 401)
        self.assertEqual(self.client.post('/api/auth/login', json={'email':user.email, 'password':'secret123'}).status_code, 401)
        response = self.client.get('/api/users/?q=Edited&role=employer&is_active=false', headers=self.headers)
        self.assertEqual([u['id'] for u in response.json()], [user_id])
        self.assertEqual(self.client.put(f'/api/users/{user_id}', headers=self.headers, json={'is_active':True}).status_code, 200)
        self.assertEqual(self.client.get('/api/auth/me', headers=self.auth(user)).status_code, 200)
        self.assertEqual(self.client.delete(f'/api/users/{user_id}', headers=self.headers).status_code, 200)
        self.assertTrue(self.session.get(User, user_id).is_deleted)
        self.assertEqual(self.client.get('/api/auth/me', headers=self.auth(user)).status_code, 401)
        self.assertEqual(self.client.get('/api/users/?q=Edited', headers=self.headers).json(), [])

    def test_admin_permissions_and_self_protection(self):
        self.assertEqual(self.client.get('/api/users/').status_code, 401)
        candidate_headers = self.auth(self.candidate)
        self.assertEqual(self.client.get('/api/users/', headers=candidate_headers).status_code, 403)
        payload = {'email':'x@example.com', 'full_name':'X', 'password':'secret123'}
        self.assertEqual(self.client.post('/api/users/', headers=candidate_headers, json=payload).status_code, 403)
        self.assertEqual(self.client.put(f'/api/users/{self.admin.id}', headers=self.headers, json={'is_active':False}).status_code, 400)
        self.assertEqual(self.client.put(f'/api/users/{self.admin.id}', headers=self.headers, json={'role':'candidate'}).status_code, 400)
        self.assertEqual(self.client.delete(f'/api/users/{self.admin.id}', headers=self.headers).status_code, 400)
        self.assertEqual(self.client.put(f'/api/users/{self.candidate.id}', headers=self.headers, json={'role':None}).status_code, 422)

    def test_profile_phone_and_password_are_saved(self):
        headers = self.auth(self.candidate)
        self.assertEqual(self.client.put('/api/auth/profile', headers=headers, json={'old_password':'wrong', 'new_password':'changed123'}).status_code, 400)
        response = self.client.put('/api/auth/profile', headers=headers, json={'phone':'0901234567', 'old_password':'secret123', 'new_password':'changed123'})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()['phone'], '0901234567')
        self.assertEqual(self.client.post('/api/auth/login', json={'email':self.candidate.email, 'password':'changed123'}).status_code, 200)
        self.assertEqual(self.client.post('/api/auth/login', json={'email':self.candidate.email, 'password':'secret123'}).status_code, 401)

    def test_refresh_tokens_cannot_authorize_account_mutations(self):
        headers = {'Authorization':'Bearer ' + create_refresh_token({'sub':str(self.admin.id)})}
        self.assertEqual(self.client.get('/api/users/', headers=headers).status_code, 401)

    def test_cv_analysis_public_and_authenticated_snapshot(self):
        payload = {'cv_text':'Python SQL Git Docker FastAPI developer', 'target_role':'Python Developer'}
        public = self.client.post('/api/cv/analyze', json=payload)
        self.assertEqual(public.status_code, 200, public.text)
        response = self.client.post('/api/cv/analyze', headers=self.auth(self.candidate), json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        snapshot = self.client.get('/api/cv/my-snapshot', headers=self.auth(self.candidate))
        self.assertEqual(snapshot.status_code, 200, snapshot.text)
        self.assertEqual(snapshot.json()['user_id'], self.candidate.id)
        self.assertTrue(self.candidate.latest_cv_analysis)

    def test_existing_routes_remain_available(self):
        for path in ['/health', '/api/jobs/', '/api/skills/', '/api/surveys/', '/api/courses/']:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, f'{path}: {response.text}')
        # KPI predates dependency injection and opens SessionLocal directly.
        with patch('src.database.SessionLocal', return_value=self.session):
            self.assertEqual(self.client.get('/api/kpi', headers=self.headers).status_code, 200)


if __name__ == '__main__':
    unittest.main()
