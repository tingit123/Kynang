import unittest
import test_merge
from src.models.notification import Notification


class NotificationTests(unittest.TestCase):
    setUp = test_merge.MergeIntegrationTests.setUp
    tearDown = test_merge.MergeIntegrationTests.tearDown
    auth = test_merge.MergeIntegrationTests.auth

    def test_only_admin_can_publish(self):
        payload = {'title':'Thông báo mới','content':'Nội dung thông báo'}
        self.assertEqual(self.client.post('/api/notifications/',json=payload).status_code,401)
        for role in ['candidate','employer','provider']:
            self.candidate.role = role
            self.session.commit()
            self.assertEqual(self.client.post('/api/notifications/',headers=self.auth(self.candidate),json=payload).status_code,403)
        result = self.client.post('/api/notifications/',headers=self.headers,json=payload)
        self.assertEqual(result.status_code,201,result.text)
        self.assertEqual(self.session.query(Notification).count(),1)

    def test_public_list_dates_content_and_pagination(self):
        self.assertEqual(self.client.get('/api/notifications/').json()['items'],[])
        for title in ['First','Second']:
            result = self.client.post('/api/notifications/',headers=self.headers,json={'title':title,'content':'Dòng 1\nDòng 2 <script>alert(1)</script>'})
            self.assertEqual(result.status_code,201,result.text)
            self.assertTrue(result.json()['created_at'].endswith(('Z','+00:00')))
        page = self.client.get('/api/notifications/?limit=1').json()
        self.assertEqual(page['total'],2)
        self.assertEqual(page['items'][0]['title'],'Second')
        self.assertIn('\n',page['items'][0]['content'])
        self.assertEqual(self.client.get('/api/notifications/?limit=1&offset=1').json()['items'][0]['title'],'First')
        self.session.expire_all()
        self.assertEqual(self.session.query(Notification).count(),2)
        self.assertEqual(self.client.get('/api/notifications/?limit=0').status_code,422)

    def test_title_and_content_validation(self):
        for payload in [{'title':' ','content':'Text'},{'title':'Title','content':'\n '},{'title':'Title'},{'title':'x'*201,'content':'Text'},{'title':'Title','content':'x'*10001}]:
            response = self.client.post('/api/notifications/',headers=self.headers,json=payload)
            self.assertEqual(response.status_code,422,response.text)
        result = self.client.post('/api/notifications/',headers=self.headers,json={'title':'  Title  ','content':'  Text  '})
        self.assertEqual(result.json()['title'],'Title')
        self.assertEqual(result.json()['content'],'Text')


if __name__ == '__main__':
    unittest.main()
