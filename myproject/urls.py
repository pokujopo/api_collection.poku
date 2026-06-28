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
from django.urls import pa
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
"""

from django.contrib import admin
from django.urls import path
from polls.views import APIDocumentationView, RegisterUserView, CustomLoginView, GenerateAPIKeyView, VideoDownloadAPIView, DownloadStatusAPIView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/docs/', APIDocumentationView.as_view(), name='api_docs'),
    path('api/v1/register/', RegisterUserView.as_view(), name='register'),
    path('api/v1/login/', CustomLoginView.as_view(), name='login'),
    path('api/v1/generate-key/', GenerateAPIKeyView.as_view(), name='generate_key'),
    path('api/v1/download/', VideoDownloadAPIView.as_view(), name='download'),
    path('api/v1/download/status/<int:pk>/', DownloadStatusAPIView.as_view(), name='download_status'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
