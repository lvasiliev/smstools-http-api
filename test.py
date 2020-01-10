#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app
import unittest
import base64

user_credentials = base64.b64encode(b'test:test').decode('utf-8')

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.client = self.app.test_client()

    def tearDown(self):
        pass

    def test_app_configuration(self):
        self.assertTrue(self.app.config['TESTING'])

    def test_unauthorized_access(self):
        response = self.client.get('/api/v1.0/sms/sent/test')
        self.assertTrue('Unauthorized access' in response.get_data(as_text=True))

    def test_authorized_access(self):
        headers = {"Authorization": "Basic {}".format(user_credentials)}
        response = self.client.get('/api/v1.0/sms/sent/test', headers=headers)
        self.assertTrue('Not found' in response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
