import hmac
import hashlib
import base64
import secrets
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions
from api_management.models import APIKey, ChannelPartner

def encrypt_secret(raw_secret):
    """Encrypts raw secret key using Django's SECRET_KEY as master key."""
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    raw_bytes = raw_secret.encode('utf-8')
    encrypted = bytes(a ^ b for a, b in zip(raw_bytes, key * (len(raw_bytes) // len(key) + 1)))
    return base64.b64encode(encrypted).decode('utf-8')

def decrypt_secret(enc_secret):
    """Decrypts secret key using Django's SECRET_KEY."""
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    decoded = base64.b64decode(enc_secret.encode('utf-8'))
    decrypted = bytes(a ^ b for a, b in zip(decoded, key * (len(decoded) // len(key) + 1)))
    return decrypted.decode('utf-8')

class HMACAPIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Extract headers
        key_id = request.META.get('HTTP_X_API_KEY_ID')
        timestamp = request.META.get('HTTP_X_TIMESTAMP')
        signature = request.META.get('HTTP_X_SIGNATURE')
        nonce = request.META.get('HTTP_X_NONCE')

        if not key_id or not timestamp or not signature or not nonce:
            return None # Skip and let other authentication classes run

        try:
            api_key = APIKey.objects.select_related('partner').get(key_id=key_id, is_active=True)
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API Key ID')

        if not api_key.partner.is_active:
            raise exceptions.AuthenticationFailed('Channel partner account is disabled')

        # Decrypt secret
        try:
            # We store the encrypted secret in the hashed_secret field for HMAC verification
            # since a one-way bcrypt hash cannot be decrypted to compute the HMAC.
            # To satisfy security, the secret is never stored in plain text.
            secret_key = decrypt_secret(api_key.hashed_secret)
        except Exception:
            raise exceptions.AuthenticationFailed('Secret key decryption failed')

        # Re-calculate HMAC signature
        # Message format: Timestamp + Nonce
        message = f"{timestamp}{nonce}".encode('utf-8')
        h = hmac.new(secret_key.encode('utf-8'), message, hashlib.sha256)
        expected_signature = h.hexdigest()

        # Secure constant-time comparison
        if not secrets.compare_digest(expected_signature, signature):
            raise exceptions.AuthenticationFailed('Invalid HMAC signature')

        # Authentication successful: return partner and key
        return (api_key.partner, api_key)
