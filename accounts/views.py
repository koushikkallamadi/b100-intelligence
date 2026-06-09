from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class JWTLoginThrottle(SimpleRateThrottle):
    scope = 'jwt_login'
    
    def get_cache_key(self, request, view):
        # Throttle by username (if provided) or client IP
        username = request.data.get('username')
        if username:
            ident = username
        else:
            ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [JWTLoginThrottle]

class TestJWTView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        return Response({
            "status": "success",
            "message": f"JWT Authentication is working! Hello, {request.user.username}.",
            "user_info": {
                "username": request.user.username,
                "email": request.user.email,
                "is_superuser": request.user.is_superuser
            }
        })
