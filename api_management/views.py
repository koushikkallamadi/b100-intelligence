import secrets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from api_management.authentication import HMACAPIKeyAuthentication, encrypt_secret
from api_management.throttling import PartnerTierThrottle
from api_management.models import ChannelPartner, APIKey, WebhookEndpoint
from api_management.tasks import log_api_usage_task
from companies.models import DimCompany, FactBalancesheet, FactProfitAndLoss
from companies.serializers import CompanyDetailsSerializer, DimCompanySerializer
from ml_engine.models import CompanyScore

# Helper to get client IP
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class PartnerCompanyDetailView(APIView):
    """
    GET /api/partner/v1/companies/{symbol}/full/
    HMAC authenticated. Throttled. Returns full financial dump for a single symbol.
    """
    authentication_classes = [HMACAPIKeyAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [PartnerTierThrottle]

    def get(self, request, symbol, *args, **kwargs):
        symbol = symbol.upper()
        partner = request.user  # Authenticated partner object
        
        try:
            company = DimCompany.objects.get(symbol=symbol)
            serializer = CompanyDetailsSerializer(company)
            response_data = serializer.data
            status_code = status.HTTP_200_OK
        except DimCompany.DoesNotExist:
            response_data = {"error": "Company symbol not found"}
            status_code = status.HTTP_404_NOT_FOUND

        # Log request asynchronously
        log_api_usage_task.delay(
            partner_id=partner.id,
            endpoint=f"GET /api/partner/v1/companies/{symbol}/full/",
            ip_address=get_client_ip(request),
            status_code=status_code
        )
        return Response(response_data, status=status_code)

class PartnerBulkFinancialsView(APIView):
    """
    GET /api/partner/v1/bulk-financials/
    HMAC authenticated. Throttled. Returns multi-company details.
    """
    authentication_classes = [HMACAPIKeyAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [PartnerTierThrottle]

    def get(self, request, *args, **kwargs):
        partner = request.user
        symbols_str = request.query_params.get('symbols', '')
        if not symbols_str:
            return Response({"error": "symbols query parameter is required"}, status=400)

        symbols = [s.strip().upper() for s in symbols_str.split(',') if s.strip()]
        companies = DimCompany.objects.filter(symbol__in=symbols)
        serializer = CompanyDetailsSerializer(companies, many=True)
        
        log_api_usage_task.delay(
            partner_id=partner.id,
            endpoint=f"GET /api/partner/v1/bulk-financials/?symbols={symbols_str}",
            ip_address=get_client_ip(request),
            status_code=200
        )
        return Response(serializer.data)

class PartnerScreenerView(APIView):
    """
    GET /api/partner/v1/screener/
    HMAC authenticated. Throttled. Screener API.
    """
    authentication_classes = [HMACAPIKeyAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [PartnerTierThrottle]

    def get(self, request, *args, **kwargs):
        partner = request.user
        min_roe = request.query_params.get('min_roe', None)
        max_de = request.query_params.get('max_de', None)
        sector = request.query_params.get('sector', None)
        
        companies_qs = DimCompany.objects.all()
        if sector:
            companies_qs = companies_qs.filter(sector__sector_name=sector)
        if min_roe:
            companies_qs = companies_qs.filter(roe_percentage__gte=float(min_roe))

        results = []
        for c in companies_qs:
            # Leverage check
            latest_bs = FactBalancesheet.objects.filter(symbol=c).order_by('-year__sort_order').first()
            de_val = float(latest_bs.debt_to_equity or 0) if latest_bs else 0.0
            
            if max_de and de_val > float(max_de):
                continue
                
            results.append({
                "symbol": c.symbol,
                "company_name": c.company_name,
                "roe": float(c.roe_percentage or 0),
                "roce": float(c.roce_percentage or 0),
                "debt_to_equity": de_val,
                "sector": c.sector.sector_name if c.sector else "Other"
            })

        log_api_usage_task.delay(
            partner_id=partner.id,
            endpoint="GET /api/partner/v1/screener/",
            ip_address=get_client_ip(request),
            status_code=200
        )
        return Response(results)

class PartnerScoresView(APIView):
    """
    GET /api/partner/v1/scores/
    HMAC authenticated. Throttled. Returns all health scores.
    """
    authentication_classes = [HMACAPIKeyAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [PartnerTierThrottle]

    def get(self, request, *args, **kwargs):
        partner = request.user
        scores = CompanyScore.objects.all()
        results = [{
            "symbol": s.symbol_id,
            "health_score": float(s.health_score),
            "health_label": s.health_label,
            "profitability": float(s.profitability_score),
            "growth": float(s.growth_score),
            "solvency": float(s.solvency_score),
            "liquidity": float(s.liquidity_score),
            "efficiency": float(s.efficiency_score),
            "scale": float(s.scale_score)
        } for s in scores]

        log_api_usage_task.delay(
            partner_id=partner.id,
            endpoint="GET /api/partner/v1/scores/",
            ip_address=get_client_ip(request),
            status_code=200
        )
        return Response(results)

class APIKeyCreateView(APIView):
    """
    POST /api/partner/v1/keys/
    Public. Creates a new API key and returns key secret ONCE.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        partner_name = request.data.get('partner_name')
        tier = request.data.get('tier', 'BASIC')

        if not partner_name:
            return Response({"error": "partner_name is required"}, status=400)

        # Create partner
        partner = ChannelPartner.objects.create(name=partner_name, tier=tier)

        # Create key
        key_id = secrets.token_hex(16)
        raw_secret = secrets.token_urlsafe(32)

        api_key = APIKey(key_id=key_id, partner=partner)
        # Store encrypted
        api_key.hashed_secret = encrypt_secret(raw_secret)
        api_key.save()

        return Response({
            "partner_id": partner.id,
            "partner_name": partner.name,
            "tier": partner.tier,
            "key_id": key_id,
            "secret_key": raw_secret,
            "note": "Save this secret key now. It will never be shown again!"
        }, status=status.HTTP_201_CREATED)

class WebhookSubscriptionView(APIView):
    """
    POST /api/partner/v1/webhooks/
    HMAC authenticated. Throttled. Subscribe to event topics.
    """
    authentication_classes = [HMACAPIKeyAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [PartnerTierThrottle]

    def post(self, request, *args, **kwargs):
        partner = request.user
        url = request.data.get('url')
        events = request.data.get('events', 'score_updated') # comma-separated

        if not url:
            return Response({"error": "url is required"}, status=400)

        secret = secrets.token_urlsafe(24)
        subscription = WebhookEndpoint.objects.create(
            partner=partner,
            url=url,
            events=events,
            secret=secret
        )

        return Response({
            "webhook_id": subscription.id,
            "url": subscription.url,
            "events": subscription.events,
            "signing_secret": secret,
            "note": "Incoming requests will be signed with this secret in X-Webhook-Signature."
        }, status=status.HTTP_201_CREATED)
