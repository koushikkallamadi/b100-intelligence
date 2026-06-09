from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    # API endpoints
    path('api/v1/', include('companies.urls')),
    path('api/', include('api_management.urls')),
    path('api/accounts/', include('accounts.urls')),
    # Schema and Swagger
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Frontend Pages
    path('', include('dashboard.urls')),
]
