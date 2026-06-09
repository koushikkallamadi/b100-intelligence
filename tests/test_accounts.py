from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

# Python 3.14 Django 4.2 Compatibility Patch:
import django.test.client
django.test.client.store_rendered_templates = lambda *args, **kwargs: None

class JWTAuthTestCase(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        
        # Create standard test user
        self.username = "testuser"
        self.password = "securepassword123"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@example.com"
        )
        self.token_url = reverse('token_obtain_pair')
        self.test_url = reverse('test_jwt')

    def test_obtain_token_success(self):
        payload = {
            "username": self.username,
            "password": self.password
        }
        response = self.client.post(self.token_url, payload, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_obtain_token_throttling(self):
        payload = {
            "username": self.username,
            "password": self.password
        }
        
        # Make 5 successful/valid requests (limit is 5/min)
        for i in range(5):
            response = self.client.post(self.token_url, payload, content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # The 6th request should trigger throttle and return HTTP 429
        response = self.client.post(self.token_url, payload, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_access_protected_endpoint_without_token(self):
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_with_valid_token(self):
        payload = {
            "username": self.username,
            "password": self.password
        }
        token_response = self.client.post(self.token_url, payload, content_type='application/json')
        access_token = token_response.json()["access"]

        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }
        response = self.client.get(self.test_url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "success")
        self.assertIn("testuser", response.json()["message"])
