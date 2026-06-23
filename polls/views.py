"""
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.models import APIKey

# 1. Endpoint ya Login ya Kawaida (Inatoa Normal Token)
# Hii class inakuja ndani ya DRF, mtumiaji anapost username na password, inampa Token.
from rest_framework_api_key.permissions import HasAPIKey # Mlinzi wetu wa API Key
from .serializers import TestSerializer
from .tasks import download_youtube_video_task # Task yako ya Celery

class VideoDownloadAPIView(APIView):
    # Swichi ya KUZIMA JWT/Normal Token kwa ajili ya hii View pekee
    authentication_classes = [] 
    
    # Swichi ya KUWASHA ulinzi wa API Key pekee
    permission_classes = [HasAPIKey]

    def post(self, request):
        # Validisha data zinazokuja (link na name)
        serializer = TestSerializer(data=request.data)
        
        if serializer.is_valid():
            # Save data kwenye database (Haitadai login ya user)
            instance = serializer.save()
            
            # Amsha mitambo ya Celery kwa nyuma ya pazia ipige kazi
            download_youtube_video_task.delay(instance.link, instance.name)
            
            return Response({
                "status": "Success",
                "message": "API Key imekubaliwa! Kazi ya kudownload imeanza kwa nyuma.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VideoDownloadAPIView(APIView):
    # LAZIMA iwe tupu kabisa ili isitegemee Token za login ya kawaida
    authentication_classes = [] 
    # Mkabidhi mlinzi wa API Key
    permission_classes = [HasAPIKey] 

    def post(self, request):
        serializer = TestSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            download_youtube_video_task.delay(instance.link, instance.name)
            return Response({
                "status": "Success",
                "message": "API Key imekubaliwa! Kazi imeanza."
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Tunatengeneza au tunachukua token ya huyu user
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'status': 'Success',
            'token': token.key, # <── Hii ndio Normal Token ya kutumia kuombea API Key
            'user_id': user.pk,
            'email': user.email
        })

# 2. Endpoint ya Kuomba API Key (Inalindwa na ile Normal Token)
class GenerateAPIKeyView(APIView):
    # Lazima uwe na ile Token ya login kwenye Header ili uingie hapa
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        name_kwa_ajili_ya_key = f"Key-Ya-{user.username}"
        
        # Kuzalisha API Key ya kudumu ya mteja
        api_key, generated_key = APIKey.objects.create_key(name=name_kwa_ajili_ya_key)
        
        return Response({
            "status": "Success",
            "message": "Ufunguo wako wa API Key umezalishwa kwa mafanikio!",
            "api_key": generated_key # <── Huu ndio ufunguo atakaoutumia maisha yake yote kwenye kichaka cha API
        }, status=status.HTTP_201_CREATED)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey 

from .serializers import TestSerializer
from .tasks import download_youtube_video_task 

# 1. Login ya Kawaida (Inatoa Normal Token)
class CustomLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'status': 'Success',
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

# 2. Kuomba API Key (Inahitaji Normal Token)
class GenerateAPIKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        name_kwa_ajili_ya_key = f"Key-Ya-{user.username}"
        api_key, generated_key = APIKey.objects.create_key(name=name_kwa_ajili_ya_key)
        return Response({
            "status": "Success",
            "message": "Ufunguo wako wa API Key umezalishwa kwa mafanikio!",
            "api_key": generated_key 
        }, status=status.HTTP_201_CREATED)

# 3. Kichaka cha API (Inahitaji hiyo API Key tu kwenye Header)
class VideoDownloadAPIView(APIView):
    authentication_classes = [] 
    permission_classes = [HasAPIKey] 

    def post(self, request):
        serializer = TestSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            download_youtube_video_task.delay(instance.link, instance.name)
            return Response({
                "status": "Success",
                "message": "API Key imekubaliwa! Kazi imeanza."
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.models import APIKey

from .serializers import TestSerializer
from .tasks import download_youtube_video_task 

# 1. TUNATENGENEZA MLINZI WETU WA MKONO (Custom API Key Permission)
class KhususiHasAPIKey(BasePermission):
    def has_permission(self, request, view):
        # Kamata ile key kutoka kwenye Header ya request
        user_key = request.headers.get("X-API-Key")
        
        if not user_key:
            return False
            
        # Nenda kwenye database ya APIKey kagua kama ufunguo huu upo na ni halali
        # Maktaba inatumia 'is_valid' kukagua ufunguo ulio-hashiwa
        from rest_framework_api_key.models import APIKey
        return APIKey.objects.is_valid(user_key)


# 2. LOGIN VIEW (Inabaki kama ilivyo)
class CustomLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'status': 'Success',
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

# 3. GENERATE VIEW (Inabaki kama ilivyo)
class GenerateAPIKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        name_kwa_ajili_ya_key = f"Key-Ya-{user.username}"
        api_key, generated_key = APIKey.objects.create_key(name=name_kwa_ajili_ya_key)
        return Response({
            "status": "Success",
            "message": "Ufunguo wako wa API Key umezalishwa kwa mafanikio!",
            "api_key": generated_key 
        }, status=status.HTTP_201_CREATED)

# 4. KICHAKA CHA API (Sasa hivi inatumia mlinzi wetu mpya namba 1)
class VideoDownloadAPIView(APIView):
    authentication_classes = [] 
    permission_classes = [KhususiHasAPIKey] # <── Tumeweka mlinzi wetu hapa!

    def post(self, request):
        serializer = TestSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            download_youtube_video_task.delay(instance.link, instance.name)
            return Response({
                "status": "Success",
                "message": "API Key imekubaliwa! Kazi imeanza."
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey # Mlinzi wetu wa API Key
from .serializers import TestSerializer
from .tasks import download_youtube_video_task # Task yako ya Celery
from .serializers import TestSerializer

# 1. MLINZI WETU (Custom API Key Permission)

from django.views.generic import TemplateView

class APIDocumentationView(TemplateView):
    template_name = "polls/api_docs.html"


class KhususiHasAPIKey(BasePermission):
    def has_permission(self, request, view):
        user_key = request.headers.get("X-API-Key")
        if not user_key:
            return False
        return APIKey.objects.is_valid(user_key)

# 2. LOGIN VIEW 
class CustomLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'status': 'Success',
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

# 3. GENERATE API KEY VIEW
class GenerateAPIKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        name_kwa_ajili_ya_key = f"Key-Ya-{user.username}"
        APIKey.objects.filter(name=name_kwa_ajili_ya_key).update(revoked=True)
        api_key, generated_key = APIKey.objects.create_key(name=name_kwa_ajili_ya_key)
        return Response({
            "status": "Success",
            "message": "Ufunguo wako wa API Key umezalishwa kwa mafanikio!",
            "api_key": generated_key 
        }, status=status.HTTP_201_CREATED)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TestSerializer
from .tasks import download_youtube_video_task

class VideoDownloadAPIView(APIView):
    def post(self, request):
        # 1. Pitisha data zote kwenye Serializer kwa ajili ya validation
        serializer = TestSerializer(data=request.data)
        
        if serializer.is_valid():
            # 2. Save data safi kwenye Database (Inakuwa 'Pending')
            instance = serializer.save()
            
            # 3. Sukuma ID kwenda kwenye Celery Task (Asynchronous Blast)
            download_youtube_video_task.delay(instance.id)
            
            # 4. Rudisha data iliyosaviwa kwenda Frontend hapo hapo bila kusubiri download
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""
# 4. KICHAKA CHA API (HAPA TUMETOA CELERY KWA MUDA)

class VideoDownloadAPIView(APIView):
    authentication_classes = [] 
    permission_classes = [KhususiHasAPIKey] 

    def post(self, request):
        serializer = TestSerializer(data=request.data)
        if serializer.is_valid():
            # Mfumo unasave data kwanza hapa kwenye database ya SQLite
            instance = serializer.save()
            if serializer.is_valid():
                instance = serializer.save()
                download_youtube_video_task.delay(instance.id)
                
                return Response({
                    "status": "Success",
                    "message": "API Key imekubaliwa! Kazi imeanza."
                }, status=status.HTTP_201_CREATED)
            # Badala ya kuita Celery inayokwamikisha kwa sasa, tunairudisha response hapa hapa direct!
            return Response({
                "status": "Success",
                "message": "API Key imekubaliwa 100%! Data imehifadhiwa vizuri.",
                "data": {
                    "id": instance.id,
                    "name": instance.name,
                    "link": instance.link
                }
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TestSerializer
from .tasks import download_youtube_video_task # Task yetu ya Celery

class VideoDownloadAPIView(APIView):
    def post(self, request):
        serializer = TestSerializer(data=request.data)
        
        if serializer.is_valid():
            # 1. Django inasave kwanza taarifa kwenye DB na kupata ID (Mfano: 36)
            instance = serializer.save()
            
            # 2. MSULUKANO WA KIKOMANDOO:
            # Badala ya kutumia .delay(), tunatumia .apply_async() kisha tunapiga .get()
            # Hapa Django ITASIMAMA na KUTULIA hewani, ikimsubiri Celery amalize download!
            task_result = download_youtube_video_task.apply_async(args=[instance.id])
            
            # .get() inalazimisha Django isubiri hapo hapo hadi task iishe 100%
            task_result.get() 
            
            # 3. Baada ya Celery kumaliza, tunamvuta tena huyu instance kutoka DB 
            # ili kupata data mpya baada ya Celery kubadilisha status kuwa "Success"
            instance.refresh_from_db()
            
            # 4. Tunatengeneza ile download link safi kabisa hapa hapa
            download_url = request.build_absolute_uri(f"/media/downloads/{instance.name}.mp4")
            
            # 5. Tunamwaga JSON kwa user ikiwa na kila kitu sekunde hiyo hiyo!
            return Response({
                "status": "Success",
                "message": "Video imedownloadiwa kikamilifu!",
                "id": instance.id,
                "name": instance.name,
                "link": instance.link,
                "download_link": download_url # <── MTUMIAJI ANAPOKEA HII HAPO HAPO!
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Test  # Jina la model yako
from .serializers import TestSerializer  # Serializer yako uliyoisuka

class DownloadStatusAPIView(APIView):
    def get(self, request, pk):
        try:
            # 1. Tunavuta data kutoka kwenye database (Model Instance)
            kazi = Test.objects.get(pk=pk)
            
            # 2. TUNAIKABIDHI DATA KWENYE SERIALIZER YAKO!
            # DRF inachukua hii instance na kuigeuza kuwa data ya Python primitive (Dict)
            serializer = TestSerializer(kazi)
            
            # 3. Kama unataka kuongeza ile download_link kwa nguvu kabla ya kutuma JSON
            # Tunaweza kuingiza variable mpya ndani ya data iliyosafishwa na serializer
            ramani_ya_json = serializer.data
            
            if kazi.status == "Success":
                # request.build_absolute_uri inatengeneza 'http://127.0.0.1:8000/media/...'
                ramani_ya_json['download_link'] = request.build_absolute_uri(
                    f"/media/downloads/{kazi.name}"
                )
            else:
                ramani_ya_json['download_link'] = None
                
            # 4. Tunarudisha JSON rasmi iliyotakaswa na Serializer
            return Response(ramani_ya_json, status=status.HTTP_200_OK)
            
        except Test.DoesNotExist:
            return Response({
                "status": "Failed",
                "error": "Kazi yenye hiyo ID haipatikani kwenye mfumo wetu."
            }, status=status.HTTP_404_NOT_FOUND)


"""
class DownloadStatusAPIView(APIView):
    # Hapa hatuweki ulinzi mkali sana, au unaweza kuweka ile API key yetu
    def get(self, request, pk):
        try:
            # Tafuta ile rekodi kwenye database kwa kutumia ID
            kazi = Test.objects.get(pk=pk)
            
            # Kama Celery bado haijabadilisha status kuwa Success kwenye DB
            if kazi.status != "Success":
                return Response({
                    "status": "Processing",
                    "message": "Video bado inashushwa kutoka YouTube, subiri kidogo..."
                })
            
            # Kama imeisha, tunatengeneza link rasmi ya download
            download_url = request.build_absolute_uri(f"/media/downloads/{kazi.name}.mp4")
            
            return Response({
                "status": "Completed",
                "video_name": kazi.name,
                "download_link": download_url # <── HII NDIO LINK YA USER!
            })
            
        except VideoDownloadModel.DoesNotExist:
            return Response({"error": "Kazi haipatikani"}, status=404)
            
"""