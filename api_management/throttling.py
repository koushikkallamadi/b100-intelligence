from django.core.cache import cache
from rest_framework import throttling
from rest_framework import exceptions
import time

class PartnerTierThrottle(throttling.BaseThrottle):
    def allow_request(self, request, view):
        # Ensure partner is authenticated via HMAC
        if not request.user or not isinstance(request.user, getattr(request.user.__class__, '__class__', object)):
            # If not authenticated as a partner (e.g. anonymous or regular user), let regular throttles handle it
            return True

        partner = request.user
        tier = getattr(partner, 'tier', 'BASIC')
        partner_id = getattr(partner, 'id', 'anonymous')

        # Define limits per period (minute, hour, day)
        limits = {
            'BASIC': {'min': 10, 'hour': 100, 'day': 500},
            'PRO': {'min': 60, 'hour': 1000, 'day': 10000},
            'ENTERPRISE': {'min': 300, 'hour': 10000, 'day': 100000},
        }

        tier_limits = limits.get(tier, limits['BASIC'])
        periods = [
            ('min', 60, tier_limits['min']),
            ('hour', 3600, tier_limits['hour']),
            ('day', 86400, tier_limits['day']),
        ]

        # Check all periods in Redis
        current_time = int(time.time())
        for label, seconds, limit in periods:
            # Build key (e.g. throttle_partner_1_min)
            # Group keys in buckets by dividing time to standard windows or simply incrementing with expiration
            # Using windowed key ensures simple atomic expiration
            window_bucket = current_time // seconds
            key = f"throttle_partner_{partner_id}_{label}_{window_bucket}"
            
            # Increment and set TTL on new keys
            count = cache.get(key)
            if count is None:
                cache.set(key, 1, timeout=seconds)
            else:
                if count >= limit:
                    # Rate limit exceeded
                    return False
                cache.incr(key)

        return True

    def wait(self):
        # Optional: return time to wait
        return 60
