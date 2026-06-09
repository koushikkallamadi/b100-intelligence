from django.urls import path, include
from rest_framework.routers import DefaultRouter
from companies.views import CompanyViewSet, CompanyDetailView, CompanyChartsView

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='companies')

urlpatterns = [
    path('companies/<str:symbol>/full/', CompanyDetailView.as_view(), name='company-detail'),
    path('companies/<str:symbol>/charts/', CompanyChartsView.as_view(), name='company-charts'),
    path('', include(router.urls)),
]
