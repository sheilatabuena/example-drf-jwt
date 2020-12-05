"""bus project URL Configuration

    Contains urls to the admin, to simplejwt, and to message_bus

"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views

from message_bus.views import JWTLogin


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),
    path('bus/', include(('message_bus.urls', 'message_bus'), namespace='bus')),
    path('login/', JWTLogin.as_view(), name='jwt_login')
]
