import unittest
import os
from unittest.mock import patch
import test_merge
from src.models.job import JobPosting
from src.models.skill import SkillCatalog
from src.models.user import User
from src.core.security import create_access_token


class SecurityAuditTests(unittest.TestCase):
    setUp = test_merge.MergeIntegrationTests.setUp
    tearDown = test_merge.MergeIntegrationTests.tearDown
    auth = test_merge.MergeIntegrationTests.auth

    def test_public_registration_cannot_create_admin(self):
        response = self.client.post('/api/auth/register',json={'email':'attacker@example.com','password':'secret123','full_name':'Attacker','role':'admin'})
        self.assertIn(response.status_code,[403,422],response.text)
        self.assertIsNone(self.session.query(User).filter(User.email=='attacker@example.com').first())

    def test_guest_cannot_delete_or_spoof_crawler(self):
        job = JobPosting(title='Protected',company='Company',industry='IT',employer_id=self.admin.id)
        self.session.add(job);self.session.commit()
        response = self.client.delete(f'/api/jobs/{job.id}')
        self.assertEqual(response.status_code,401,response.text)
        self.assertFalse(job.is_deleted)
        payload={'title':'Forged','company':'Company','industry':'IT','source_platform':'TopCV'}
        self.assertEqual(self.client.post('/api/jobs/',json=payload).status_code,401)

    def test_anonymous_skill_write_is_rejected(self):
        skill=SkillCatalog(skill_name='Python',industry='IT',gap_pct=10)
        self.session.add(skill);self.session.commit()
        self.assertEqual(self.client.put(f'/api/skills/{skill.id}',json={'gap_pct':999}).status_code,401)

    def test_password_reset_does_not_disclose_otp_or_account_existence(self):
        known=self.client.post('/api/auth/forgot-password',json={'email':self.candidate.email})
        unknown=self.client.post('/api/auth/forgot-password',json={'email':'unknown@example.com'})
        self.assertNotIn('debug_otp',known.json())
        self.assertEqual(known.json()['message'],unknown.json()['message'])

    def test_jwt_has_unique_token_ids_and_refresh_can_rotate_immediately(self):
        first=create_access_token({'sub':str(self.admin.id)})
        second=create_access_token({'sub':str(self.admin.id)})
        self.assertNotEqual(first,second)
        result=self.client.post('/api/auth/login',json={'email':self.candidate.email,'password':'secret123'})
        old=result.json()['refresh_token']
        refreshed=self.client.post('/api/auth/refresh',json={'refresh_token':old})
        self.assertEqual(refreshed.status_code,200,refreshed.text)
        new=refreshed.json()['refresh_token'];self.assertNotEqual(old,new)
        self.assertEqual(self.client.post('/api/auth/refresh',json={'refresh_token':new}).status_code,200)
        self.assertEqual(self.client.post('/api/auth/refresh',json={'refresh_token':old}).status_code,401)

    def test_malformed_subject_returns_401_instead_of_500(self):
        token=create_access_token({'sub':'not-a-number'})
        result=self.client.get('/api/auth/me',headers={'Authorization':'Bearer '+token})
        self.assertEqual(result.status_code,401,result.text)

    def test_survey_stats_route_is_not_shadowed_by_student_code(self):
        response=self.client.get('/api/surveys/stats')
        self.assertEqual(response.status_code,200,response.text)
        self.assertIn('total',response.json())

    def test_internal_token_allows_worker_but_not_wrong_key(self):
        payload={'title':'Crawler job','company':'Company','industry':'IT','source_platform':'TopCV'}
        with patch.dict(os.environ, {'INTERNAL_API_TOKEN':'qa-internal-token'}):
            self.assertEqual(self.client.post('/api/jobs/',headers={'X-Worker-Token':'wrong'},json=payload).status_code,401)
            result=self.client.post('/api/jobs/',headers={'X-Worker-Token':'qa-internal-token'},json=payload)
            self.assertEqual(result.status_code,201,result.text)
            self.assertIsNone(result.json()['employer_id'])
            skill=SkillCatalog(skill_name='Python',industry='IT',gap_pct=10)
            self.session.add(skill);self.session.commit()
            result=self.client.put(f'/api/skills/{skill.id}',headers={'X-Worker-Token':'qa-internal-token'},json={'gap_pct':20})
            self.assertEqual(result.status_code,200,result.text)

    def test_job_ownership_and_application_lifecycle(self):
        self.admin.role='employer';self.session.commit()
        payload={'title':'Python Developer','company':'Company','industry':'IT','skills':['Python']}
        created=self.client.post('/api/jobs/',headers=self.headers,json=payload)
        self.assertEqual(created.status_code,201,created.text)
        job_id=created.json()['id']
        self.assertEqual(created.json()['employer_id'],self.admin.id)
        applied=self.client.post(f'/api/jobs/{job_id}/apply',headers=self.auth(self.candidate),json={'cv_snapshot_text':'Python CV'})
        self.assertEqual(applied.status_code,201,applied.text)
        self.assertEqual(self.client.post(f'/api/jobs/{job_id}/apply',headers=self.auth(self.candidate)).status_code,400)
        self.assertEqual(len(self.client.get(f'/api/jobs/{job_id}/applications',headers=self.headers).json()),1)
        self.assertEqual(self.client.get(f'/api/jobs/{job_id}/applications',headers=self.auth(self.candidate)).status_code,403)
        self.candidate.role='employer';self.session.commit()
        self.assertEqual(self.client.delete(f'/api/jobs/{job_id}',headers=self.auth(self.candidate)).status_code,403)
        self.assertEqual(self.client.delete(f'/api/jobs/{job_id}',headers=self.headers).status_code,200)
        self.assertEqual(self.client.get(f'/api/jobs/{job_id}').status_code,404)

    def test_otp_is_invalidated_after_five_wrong_attempts(self):
        from src.routers.auth import RESET_OTP_STORE
        from datetime import datetime, timedelta
        RESET_OTP_STORE[self.candidate.email]={'otp':'123456','expires_at':datetime.now()+timedelta(minutes=1),'attempts':0}
        payload={'email':self.candidate.email,'otp':'000000','new_password':'changed123'}
        for _ in range(5):
            self.assertEqual(self.client.post('/api/auth/reset-password',json=payload).status_code,400)
        self.assertNotIn(self.candidate.email,RESET_OTP_STORE)
        self.assertEqual(self.client.post('/api/auth/reset-password',json={**payload,'otp':'123456'}).status_code,400)
