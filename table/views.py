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
from .models import Test
from .serializers import TestSerializer




# ==========================================
# 0. API DOCUMENTATION VIEW
# ==========================================
class APIDocumentationView(TemplateView):
    template_name = "polls/api_docs.html"


# ==========================================
# 1. MLINZI WETU (Custom API Key Permission)
# ==========================================
class KhususiHasAPIKey(BasePermission):
    def has_permission(self, request, view):
        # Inasoma ufunguo kutoka kwenye Header ya request: X-API-Key
        user_key = request.headers.get("X-API-Key")
        if not user_key:
            return False
        return APIKey.objects.is_valid(user_key)


# ==========================================
# 2. REGISTER USER VIEW (Mpya ya Kupokea User Supabase)
# ==========================================
class RegisterUserView(APIView):
    permission_classes = [AllowAny]  # Kila mtu anaweza kujisajili bila vikwazo

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not password:
            return Response({
                "status": "Failed",
                "error": "Username na password ni lazima viwepo!"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Angalia kama mtumiaji tayari yupo kule Supabase auth_user
        if User.objects.filter(username=username).exists():
            return Response({
                "status": "Failed",
                "error": "Mtumiaji mwenye jina hili tayari ameshasajiliwa!"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Unda user mpya
            user = User.objects.create_user(username=username, email=email, password=password)
            
            # Tengeneza Token ya huyu user kwa ajili ya mambo ya Login/Frontend baadae
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                "status": "Success",
                "message": "Mtumiaji amesajiliwa kwa mafanikio kule Supabase!",
                "user_id": user.pk,
                "username": user.username,
                "token": token.key
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "status": "Failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==========================================
# 3. LOGIN VIEW
# ==========================================
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


# ==========================================
# 4. GENERATE API KEY VIEW
# ==========================================
class GenerateAPIKeyView(APIView):
    permission_classes = [IsAuthenticated]  # Lazima uwe ume-login (uwe na Token) ili upate API Key

    def post(self, request):
        user = request.user
        name_kwa_ajili_ya_key = f"Key-Ya-{user.username}"
        
        # Revoke (futa nguvu ya) key zote za zamani za huyu user ili abaki na moja tu hai
        APIKey.objects.filter(name=name_kwa_ajili_ya_key).update(revoked=True)
        
        # Zalisha Ufunguo mpya halisi
        api_key, generated_key = APIKey.objects.create_key(name=name_kwa_ajili_ya_key)
        
        return Response({
            "status": "Success",
            "message": "Ufunguo wako wa API Key umezalishwa kwa mafanikio! Linda ufunguo huu, hauonekani tena.",
            "api_key": generated_key 
        }, status=status.HTTP_201_CREATED)

