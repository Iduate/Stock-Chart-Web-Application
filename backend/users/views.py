from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, UserProfile, Subscription
from .serializers import UserSerializer, UserProfileSerializer, SubscriptionSerializer
from .oauth_utils import verify_google_token, get_or_create_google_user
import uuid
import json

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
        
        # Django uses username field for authentication, but our users login with email
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None
            
        if user and user.is_active:
            # Ensure Django session-based authentication is active
            login(request, user)
            # Generate session token (simplified - in production use proper JWT)
            token = str(uuid.uuid4())
            
            # Store token in session or cache (simplified approach)
            request.session['auth_token'] = token
            request.session['user_id'] = user.id
            
            return Response({
                'access_token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'user_type': user.user_type,
                    'subscription_status': user.subscription_status,
                    'free_access_count': user.free_access_count,
                    'prediction_accuracy': float(user.prediction_accuracy),
                    'total_profit': float(user.total_profit)
                },
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
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        referred_by = request.data.get('referred_by')
        
        if not all([username, email, password]):
            return Response({
                'message': '모든 필수 정보를 입력해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({
                'message': '이미 사용 중인 이메일입니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(username=username).exists():
            return Response({
                'message': '이미 사용 중인 사용자명입니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create user
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password),  # Hash the password
                user_type='free',  # Default to free user
                subscription_status='inactive'
            )
            
            # Generate referral code
            user.referral_code = f"REF{user.id:06d}"
            
            # Handle referral
            if referred_by:
                try:
                    referrer = User.objects.get(referral_code=referred_by)
                    user.referred_by = referrer
                except User.DoesNotExist:
                    pass  # Invalid referral code, ignore
            
            user.save()
            
            # Create profile
            UserProfile.objects.create(user=user)
            
            return Response({
                'message': '회원가입이 완료되었습니다.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'user_type': user.user_type,
                    'referral_code': user.referral_code
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'message': '회원가입 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        token = request.data.get('id_token')
        if not token:
            return Response({
                'message': 'ID 토큰이 필요합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify the token
        user_info = verify_google_token(token)
        if not user_info:
            return Response({
                'message': '유효하지 않은 Google 토큰입니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create the user
        user, created = get_or_create_google_user(user_info)
        if not user:
            return Response({
                'message': '사용자 생성에 실패했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Log the user in to enable SessionAuthentication and set a token for compatibility
        import uuid
        login(request, user)
        token = str(uuid.uuid4())
        request.session['auth_token'] = token
        request.session['user_id'] = user.id
        
        # Return user data and token
        return Response({
            'access_token': token,
            'user': UserSerializer(user).data,
            'message': '구글 로그인에 성공했습니다.',
            'is_new_user': created
        })

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
