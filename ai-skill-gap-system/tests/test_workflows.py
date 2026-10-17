import unittest
import test_merge
from src.models.skill import SkillCatalog
from src.models.survey import SurveyResponse, SurveySkillRating
from src.models.course import CourseRecommendation


class WorkflowTests(unittest.TestCase):
    setUp = test_merge.MergeIntegrationTests.setUp
    tearDown = test_merge.MergeIntegrationTests.tearDown
    auth = test_merge.MergeIntegrationTests.auth

    def seed_skill(self):
        skill = SkillCatalog(skill_name='Python', industry='IT', demand_pct=50, supply_pct=30, gap_pct=20)
        self.session.add(skill)
        self.session.commit()
        return skill.id

    def test_create_profile_detail_and_search(self):
        skill_id = self.seed_skill()
        payload = {'student_code':'HS-123', 'full_name':'Nguyen Van An', 'major':'IT', 'institution':'CTU', 'year_of_study':4, 'skills':[{'skill_id':skill_id,'self_rating':82}]}
        response = self.client.post('/api/surveys/', headers=self.headers, json=payload)
        self.assertEqual(response.status_code,201,response.text)
        self.assertEqual(response.json()['skills'][0]['rating'],82)
        detail = self.client.get('/api/surveys/HS-123')
        self.assertEqual(detail.status_code,200)
        self.assertEqual(detail.json()['full_name'],'Nguyen Van An')
        self.assertEqual(len(self.client.get('/api/surveys/?q=HS-123').json()),1)
        self.assertEqual(self.client.post('/api/surveys/',headers=self.headers,json=payload).status_code,409)
        self.assertEqual(self.session.query(SurveyResponse).count(),1)
        self.assertEqual(self.session.query(SurveySkillRating).count(),1)

    def test_profile_validation_permissions_and_auto_code(self):
        skill_id = self.seed_skill()
        self.assertEqual(self.client.post('/api/surveys/',json={'full_name':'An'}).status_code,401)
        self.assertEqual(self.client.post('/api/surveys/',headers=self.auth(self.candidate),json={'full_name':'An'}).status_code,403)
        for payload in [
            {'full_name':'  '},
            {'full_name':'An','skills':[{'skill_id':skill_id,'self_rating':101}]},
            {'full_name':'An','skills':[{'skill_id':999,'self_rating':65}]},
            {'full_name':'An','skills':[{'skill_id':skill_id,'self_rating':65}]*2},
        ]:
            self.assertEqual(self.client.post('/api/surveys/',headers=self.headers,json=payload).status_code,422)
        result=self.client.post('/api/surveys/',headers=self.headers,json={'full_name':'An'})
        self.assertEqual(result.status_code,201,result.text)
        self.assertTrue(result.json()['student_code'].startswith('HS'))
        self.assertEqual(result.json()['skills'],[])

    def test_course_creation_and_validation(self):
        skill_id = self.seed_skill()
        payload={'skill_id':skill_id,'course_name':'Python Practice','platform':'Training Center','url':'https://example.com/python'}
        self.assertEqual(self.client.post('/api/courses/',json=payload).status_code,401)
        self.assertEqual(self.client.post('/api/courses/',headers=self.auth(self.candidate),json=payload).status_code,403)
        response=self.client.post('/api/courses/',headers=self.headers,json=payload)
        self.assertEqual(response.status_code,201,response.text)
        self.assertEqual(response.json()['status'],'approved')
        self.assertEqual(self.client.get('/api/courses/').json()[0]['course_name'],'Python Practice')
        for patch in [{'url':'javascript:alert(1)'},{'course_name':'   '},{'skill_id':999},{'priority':0}]:
            response=self.client.post('/api/courses/',headers=self.headers,json={**payload,**patch})
            self.assertIn(response.status_code,[404,422],response.text)
        self.assertEqual(self.session.query(CourseRecommendation).count(),1)

    def test_provider_course_stays_pending(self):
        self.candidate.role='provider'; self.session.commit()
        response=self.client.post('/api/courses/',headers=self.auth(self.candidate),json={'skill_id':self.seed_skill(),'course_name':'Course','platform':'Center','url':'https://example.com'})
        self.assertEqual(response.status_code,201,response.text)
        self.assertEqual(response.json()['status'],'pending')
        self.assertEqual(response.json()['provider_id'],self.candidate.id)


if __name__ == '__main__':
    unittest.main()
