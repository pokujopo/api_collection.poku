import os
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from rest_framework_api_key.models import APIKey
from table.models import Test
from table.serializers import TestSerializer
from .tasks import download_youtube_video_task  # Task yako ya zamani ya Celery inayodownload faili la ndani
from table.views import KhususiHasAPIKey
from rest_framework.throttling import ScopedRateThrottle
# ==========================================
# 5. VIDEO DOWNLOAD API VIEW (Iliyofungwa Ulinzi wa API Key)
# ==========================================
class VideoDownloadAPIView(APIView):
    # UKUTA WA ULINZI: Request lazima ije na X-API-Key halali kwenye Header!

    permission_classes = [KhususiHasAPIKey]
    throttle_classes = [ScopedRateThrottle]
    
    # 3. Hapa ndio unaweka jina la plugin (Scope) linaloendana na settings.py
    throttle_scope = 'media_downloader'
    def post(self, request):
        # 1. Pitisha data zote kwenye Serializer kwa ajili ya validation
        serializer = TestSerializer(data=request.data)
        
        if serializer.is_valid():
            # 2. Save data safi kwenye Database ya Supabase (Inakuwa 'Pending')
            instance = serializer.save()
            
            # 3. Sukuma ID kwenda kwenye Celery Task (Asynchronous Blast ya ma-file ya ndani)
            download_youtube_video_task.delay(instance.id)
            
            # 4. Rudisha data iliyosaviwa kwenda Frontend hapo hapo bila kusubiri download
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 6. DOWNLOAD STATUS API VIEW
# ==========================================
class DownloadStatusAPIView(APIView):
    # Hii inaachwa wazi au unaweza kuweka permission_classes=[KhususiHasAPIKey] ukitaka kulinda status pia
    def get(self, request, pk):
        try:
            # 1. Tunavuta data kutoka kwenye database (Supabase Model Instance)
            kazi = Test.objects.get(pk=pk)
            
            # 2. TUNAIKABIDHI DATA KWENYE SERIALIZER YAKO!
            serializer = TestSerializer(kazi)
            ramani_ya_json = serializer.data
            
            # 3. Kama kazi imefanikiwa, tunatengeneza link ya ukweli ya kupakulia kutoka diski ya Render
            if kazi.status == "Success":
                ramani_ya_json['download_link'] = request.build_absolute_uri(
                    f"/media/downloads/{kazi.name}"
                )
            else:
                ramani_ya_json['download_link'] = None
                
            # 4. Tunarudisha JSON rasmi iliyotakaswa
            return Response(ramani_ya_json, status=status.HTTP_200_OK)
            
        except Test.DoesNotExist:
            return Response({
                "status": "Failed",
                "error": "Kazi yenye hiyo ID haipatikani kwenye mfumo wetu."
            }, status=status.HTTP_404_NOT_FOUND)
        
