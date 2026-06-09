from django.urls import path
from api_management.views import (
    PartnerCompanyDetailView, PartnerBulkFinancialsView, 
    PartnerScreenerView, PartnerScoresView, 
    APIKeyCreateView, WebhookSubscriptionView
)

urlpatterns = [
    path('partner/v1/companies/<str:symbol>/full/', PartnerCompanyDetailView.as_view(), name='partner-company-detail'),
    path('partner/v1/bulk-financials/', PartnerBulkFinancialsView.as_view(), name='partner-bulk-financials'),
    path('partner/v1/screener/', PartnerScreenerView.as_view(), name='partner-screener'),
    path('partner/v1/scores/', PartnerScoresView.as_view(), name='partner-scores'),
    path('partner/v1/keys/', APIKeyCreateView.as_view(), name='partner-key-create'),
    path('partner/v1/webhooks/', WebhookSubscriptionView.as_view(), name='partner-webhook-subscribe'),
]
