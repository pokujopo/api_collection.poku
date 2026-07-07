# plugins/media_downloader/urls.py
from django.urls import path
from plugins.media_downloader.api import VideoDownloadAPIView,DownloadStatusAPIView

urlpatterns = [
    # Njia yetu pendwa sasa ipo kwenye kiwango cha CBV
    path('download/', VideoDownloadAPIView.as_view(), name='media_download_endpoint'),
    path('download/status/<int:pk>/', DownloadStatusAPIView.as_view(), name='download_status'),
]