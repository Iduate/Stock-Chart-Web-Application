from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, Subscription
from .serializers import UserSerializer, UserProfileSerializer, SubscriptionSerializer
import uuid

class UserViewSet(viewsets.ModelViewSet):
    """사용자 관리 ViewSet"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class UserProfileViewSet(viewsets.ModelViewSet):
    """사용자 프로필 관리 ViewSet"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

class SubscriptionViewSet(viewsets.ModelViewSet):
    """구독 관리 ViewSet"""
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

class LoginView(APIView):
    """로그인 API"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'message': '이메일과 비밀번호를 입력해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=email, password=password)
        if user:
            # OAuth2 토큰 생성 (간단한 구현)
            token = str(uuid.uuid4())
            return Response({
                'access_token': token,
                'user': UserSerializer(user).data,
                'message': '로그인에 성공했습니다.'
            })
        else:
            return Response({
                'message': '이메일 또는 비밀번호가 올바르지 않습니다.'
            }, status=status.HTTP_401_UNAUTHORIZED)

class SignupView(APIView):
    """회원가입 API"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # 추천인 코드 생성
            user.referral_code = f"REF{user.id:06d}"
            user.save()
            
            # 프로필 생성
            UserProfile.objects.create(user=user)
            
            return Response({
                'message': '회원가입이 완료되었습니다.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'message': '회원가입에 실패했습니다.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """로그아웃 API"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({'message': '로그아웃되었습니다.'})

class VerifyTokenView(APIView):
    """토큰 검증 API"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({
            'user': UserSerializer(request.user).data,
            'message': '유효한 토큰입니다.'
        })

class GoogleOAuthView(APIView):
    """Google OAuth 로그인"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Google OAuth 구현 예정
        return Response({
            'message': 'Google 로그인 기능을 준비중입니다.'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)

class AppleOAuthView(APIView):
    """Apple OAuth 로그인"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Apple OAuth 구현 예정
        return Response({
            'message': 'Apple 로그인 기능을 준비중입니다.'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)

class CurrentUserProfileView(APIView):
    """현재 사용자 프로필 조회/수정"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            profile = request.user.userprofile
            return Response(UserProfileSerializer(profile).data)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
            return Response(UserProfileSerializer(profile).data)
    
    def put(self, request):
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
