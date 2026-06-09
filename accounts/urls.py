from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import ThrottledTokenObtainPairView, TestJWTView

urlpatterns = [
    path('token/', ThrottledTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('test-jwt/', TestJWTView.as_view(), name='test_jwt'),
]
