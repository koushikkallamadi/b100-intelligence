import hmac
import hashlib
import json
import urllib.request
from celery import shared_task
from api_management.models import APIUsageLog, WebhookEndpoint, ChannelPartner

@shared_task
def log_api_usage_task(partner_id, endpoint, ip_address, status_code):
    """
    Asynchronously log channel partner API requests.
    """
    try:
        partner = ChannelPartner.objects.get(id=partner_id) if partner_id else None
        APIUsageLog.objects.create(
            partner=partner,
            endpoint=endpoint,
            ip_address=ip_address,
            status_code=status_code
        )
        print(f"API Usage Logged: {endpoint} by Partner {partner_id}")
    except Exception as e:
        print(f"Failed to log API usage: {e}")

@shared_task
def dispatch_webhook_event_task(event_name, payload):
    """
    Deliver webhook events to active subscribers.
    Each payload is signed with HMAC-SHA256 signature in X-Webhook-Signature.
    """
    endpoints = WebhookEndpoint.objects.filter(is_active=True, events__contains=event_name)
    payload_str = json.dumps(payload)
    
    for ep in endpoints:
        # Calculate HMAC signature using the webhook secret
        signature = hmac.new(ep.secret.encode('utf-8'), payload_str.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # Dispatch HTTP POST request using standard urllib to avoid extra dependency issues
        req = urllib.request.Request(
            ep.url,
            data=payload_str.encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'X-Webhook-Event': event_name,
                'X-Webhook-Signature': signature
            },
            method='POST'
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                print(f"Webhook delivered successfully to {ep.url} for event {event_name}")
        except Exception as e:
            print(f"Failed webhook delivery to {ep.url}: {e}")
