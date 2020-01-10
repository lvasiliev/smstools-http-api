#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app
import unittest

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')

    def tearDown(self):
        pass

    def test_app_configuration(self):
        self.assertTrue(self.app.config['TESTING'])

if __name__ == '__main__':
    unittest.main()
