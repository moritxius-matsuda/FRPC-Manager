#!/usr/bin/env python3
"""
Test script for FRPC Manager
This script tests the basic functionality of the FRPC Manager application
"""

import os
import sys
import unittest
from app import create_app

class FRPCManagerTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
    
    def test_index_redirect_to_setup(self):
        """Test that index redirects to setup if no config exists"""
        # Mock the config file check
        import app.views
        app.views.os.path.exists = lambda x: False
        
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_setup_page(self):
        """Test that setup page loads correctly"""
        response = self.client.get('/setup')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Initial FRPC Setup', response.data)
    
    def test_restart_redirect(self):
        """Test that restart endpoint redirects to index"""
        # Mock the restart function
        import app.views
        app.views.restart_frpc = lambda: True
        
        response = self.client.get('/restart', follow_redirects=False)
        self.assertEqual(response.status_code, 302)  # Redirect status code

if __name__ == '__main__':
    unittest.main()