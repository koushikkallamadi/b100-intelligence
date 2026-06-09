import bcrypt
from django.db import models

class ChannelPartner(models.Model):
    TIER_CHOICES = (
        ('BASIC', 'Basic Tier'),
        ('PRO', 'Pro Tier'),
        ('ENTERPRISE', 'Enterprise Tier'),
    )
    name = models.CharField(max_length=255)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='BASIC')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return f"{self.name} ({self.tier})"

class APIKey(models.Model):
    key_id = models.CharField(max_length=50, primary_key=True)
    partner = models.ForeignKey(ChannelPartner, on_delete=models.CASCADE, related_name='api_keys')
    hashed_secret = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_secret(self, raw_secret):
        # Hash secret using bcrypt
        salt = bcrypt.gensalt()
        self.hashed_secret = bcrypt.hashpw(raw_secret.encode('utf-8'), salt).decode('utf-8')

    def check_secret(self, raw_secret):
        # Verify secret using bcrypt
        return bcrypt.checkpw(raw_secret.encode('utf-8'), self.hashed_secret.encode('utf-8'))

    def __str__(self):
        return f"Key {self.key_id} for {self.partner.name}"

class APIUsageLog(models.Model):
    partner = models.ForeignKey(ChannelPartner, on_delete=models.CASCADE, null=True, blank=True)
    endpoint = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    status_code = models.IntegerField()

    class Meta:
        db_table = 'api_usage_log'

class WebhookEndpoint(models.Model):
    partner = models.ForeignKey(ChannelPartner, on_delete=models.CASCADE, related_name='webhooks')
    url = models.URLField()
    events = models.CharField(max_length=255, default='score_updated') # comma separated: e.g. score_updated,anomaly_flagged
    secret = models.CharField(max_length=100) # secret for signing outgoing webhook requests
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Webhook for {self.partner.name} -> {self.url}"
