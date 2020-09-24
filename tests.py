import unittest
from app import app

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_only_post_page(self):
        response = self.app.get('v1/parse-date', content_type='json')
        self.assertEqual(response.status_code, 405)
        response = self.app.put('v1/parse-date', content_type='json')
        self.assertEqual(response.status_code, 405)
        response = self.app.delete('v1/parse-date', content_type='json')
        self.assertEqual(response.status_code, 405)

if __name__ == '__main__':
    unittest.main()