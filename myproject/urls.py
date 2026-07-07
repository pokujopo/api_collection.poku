"""
from django.contrib import admin
from django.urls import path
from polls.views import CustomLoginView, GenerateAPIKeyView # Rekebisha path kulingana na ulipoweka views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Sehemu ya Login (Inapokea Username/Password -> Inatema Normal Token)
    path('api/auth/login/', CustomLoginView.as_view(), name='normal_login'),
    
    # 2. Sehemu ya kuomba API Key (Inapokea Normal Token kwenye Header -> Inatema API Key)
    path('api/v1/keys/generate/', GenerateAPIKeyView.as_view(), name='generate_api_key'),
]
"""
"""
from django.contrib import admin
from django.urls import path
from polls.views import CustomLoginView, GenerateAPIKeyView
from polls.views import VideoDownloadAPIView # <── Import View yetu mpya hapa

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Sehemu za Auth (Normal Token)
    path('api/auth/login/', CustomLoginView.as_view(), name='normal_login'),
    path('api/v1/keys/generate/', GenerateAPIKeyView.as_view(), name='generate_api_key'),
    
    # ──── KICHAKA CHA API YENYEWE (Inahitaji tu API Key) ────
    path('api/v1/download/', VideoDownloadAPIView.as_view(), name='api_download_video'),
]


from django.contrib import admin
from django.urls import path
from polls.views import CustomLoginView, GenerateAPIKeyView, VideoDownloadAPIView,DownloadStatusAPIView,APIDocumentationView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', CustomLoginView.as_view(), name='normal_login'),
    path('api/v1/keys/generate/', GenerateAPIKeyView.as_view(), name='generate_api_key'),
    path('api/v1/download/', VideoDownloadAPIView.as_view(), name='api_download_video'),
    path('download/status/<int:pk>/', DownloadStatusAPIView.as_view()),
    path('api/v1/docs/', APIDocumentationView.as_view(), name='api_docs'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""

from django.contrib import admin
from django.urls import path
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import secrets

from myproject.plugin_manager import plugin_manager
# Ongeza hii import juu kabisa kwenye myproject/urls.py yako
from rest_framework_api_key.models import APIKey
from django.conf import settings
from django.conf.urls.static import static

from table.views import CustomLoginView, GenerateAPIKeyView,RegisterUserView,APIDocumentationView


# --- CAPABILITY REGISTRY ---
@api_view(['GET'])
def capability_registry_view(request):
    """Inarudisha uwezo (capabilities) wote wa platform kwa sasa"""
    return Response({
        "status": "success",
        "capabilities": plugin_manager.capabilities
    })


# --- MAIN URL ROUTER ---
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Endpoint ya kuona huduma zote zilizopo hewani
    path('api/v1/capabilities/', capability_registry_view, name='capabilities'),
    path('api/v1/register/', RegisterUserView.as_view(), name='register'),
    path('api/v1/login/', CustomLoginView.as_view(), name='login'),
    path('api/v1/docs/', APIDocumentationView.as_view(), name='api_docs'),
    
    # 2. Endpoint ya Login ya DRF (Mtu anapata Token ya kwanza hapa)
    # Atatuma POST yenye 'username' na 'password'
    path('api/v1/auth/login/', obtain_auth_token, name='api_token_auth'),
    
    # 3. Endpoint ya kuomba API Key kwa kutumia ile Token ya login
    path('api/v1/auth/generate-api-key/', GenerateAPIKeyView.as_view(), name='generate_api_key'),
]

# HAPA NDIO MOYO WA MFUMO UNAPOJIDUNGA URL ZOTE ZA MA-PLUGIN KIOTOMATIKI!
urlpatterns += plugin_manager.get_plugin_urls()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)