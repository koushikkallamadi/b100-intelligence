import hmac
import hashlib
import time
import secrets
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from api_management.models import ChannelPartner, APIKey
from api_management.authentication import encrypt_secret

# Python 3.14 Django 4.2 Compatibility Patch:
# Disable template context copying in test client which throws AttributeError: 'super' object has no attribute 'dicts'
import django.test.client
django.test.client.store_rendered_templates = lambda *args, **kwargs: None

class HMACAPITestCase(TestCase):
    def setUp(self):
        # Create partner
        self.partner = ChannelPartner.objects.create(name="Test Partner", tier="BASIC")
        
        # Create key
        self.key_id = "test_key_id"
        self.raw_secret = "test_secret_key_12345"
        self.api_key = APIKey.objects.create(
            key_id=self.key_id,
            partner=self.partner,
            hashed_secret=encrypt_secret(self.raw_secret)
        )

    def test_valid_signature(self):
        timestamp = str(int(time.time()))
        nonce = secrets.token_hex(8)
        
        # Calculate signature: HMAC-SHA256(timestamp + nonce, secret)
        message = f"{timestamp}{nonce}".encode('utf-8')
        h = hmac.new(self.raw_secret.encode('utf-8'), message, hashlib.sha256)
        signature = h.hexdigest()
        
        # API request
        url = reverse('partner-scores')
        headers = {
            'HTTP_X_API_KEY_ID': self.key_id,
            'HTTP_X_TIMESTAMP': timestamp,
            'HTTP_X_SIGNATURE': signature,
            'HTTP_X_NONCE': nonce
        }
        
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tampered_signature(self):
        timestamp = str(int(time.time()))
        nonce = secrets.token_hex(8)
        signature = "tampered_signature_value"
        
        url = reverse('partner-scores')
        headers = {
            'HTTP_X_API_KEY_ID': self.key_id,
            'HTTP_X_TIMESTAMP': timestamp,
            'HTTP_X_SIGNATURE': signature,
            'HTTP_X_NONCE': nonce
        }
        
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_missing_headers(self):
        url = reverse('partner-scores')
        # Empty headers
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
