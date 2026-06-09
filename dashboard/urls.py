from django.urls import path
from dashboard.views import (
    home_view, company_list_view, company_detail_view, 
    compare_view, screener_view, sector_view
)

urlpatterns = [
    path('', home_view, name='home'),
    path('companies/', company_list_view, name='companies'),
    path('company/<str:symbol>/', company_detail_view, name='company_detail'),
    path('compare/', compare_view, name='compare'),
    path('screener/', screener_view, name='screener'),
    path('sector/<str:name>/', sector_view, name='sector'),
]
