from django.shortcuts import get_object_or_404
from django.utils.translation import get_language, activate
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from .models import Language, Translation, UserLanguagePreference, TranslationRequest
from .serializers import (
    LanguageSerializer, TranslationSerializer, TranslationBulkSerializer,
    UserLanguagePreferenceSerializer, UserLanguagePreferenceUpdateSerializer,
    TranslationRequestSerializer, TranslationRequestCreateSerializer
)
from .services import TranslationService, LanguageDetectionService
import logging

logger = logging.getLogger(__name__)


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    """지원 언어 목록 API"""
    
    queryset = Language.objects.filter(is_active=True)
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @method_decorator(cache_page(60 * 60))  # 1시간 캐시
    def list(self, request, *args, **kwargs):
        """활성화된 언어 목록 반환"""
        return super().list(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """현재 활성화된 언어 정보 반환"""
        current_language_code = get_language() or 'ko'
        try:
            language = Language.objects.get(code=current_language_code, is_active=True)
            serializer = self.get_serializer(language)
            return Response(serializer.data)
        except Language.DoesNotExist:
            # 기본 언어 반환
            language = Language.objects.get(code='ko')
            serializer = self.get_serializer(language)
            return Response(serializer.data)


class TranslationViewSet(viewsets.ReadOnlyModelViewSet):
    """번역 데이터 API"""
    
    queryset = Translation.objects.filter(is_validated=True)
    serializer_class = TranslationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """언어별 번역 데이터 필터링"""
        queryset = self.queryset
        language_code = self.request.query_params.get('language', None)
        category = self.request.query_params.get('category', None)
        
        if language_code:
            queryset = queryset.filter(language__code=language_code)
        if category:
            queryset = queryset.filter(category=category)
            
        return queryset
    
    @method_decorator(cache_page(60 * 30))  # 30분 캐시
    def list(self, request, *args, **kwargs):
        """번역 목록 반환 (캐시 적용)"""
        return super().list(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def by_language(self, request):
        """특정 언어의 모든 번역 데이터 반환"""
        language_code = request.query_params.get('language', 'ko')
        category = request.query_params.get('category', None)
        
        try:
            language = Language.objects.get(code=language_code, is_active=True)
        except Language.DoesNotExist:
            return Response(
                {'error': 'Invalid language code'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = Translation.objects.filter(language=language, is_validated=True)
        if category:
            queryset = queryset.filter(category=category)
        
        # 딕셔너리 형태로 반환
        translations = {}
        for translation in queryset:
            translations[translation.key] = translation.value
        
        return Response({
            'language': language_code,
            'translations': translations
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def bulk_update(self, request):
        """대량 번역 업데이트 (관리자용)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = TranslationBulkSerializer(data=request.data)
        if serializer.is_valid():
            language_code = serializer.validated_data['language_code']
            translations = serializer.validated_data['translations']
            
            try:
                language = Language.objects.get(code=language_code, is_active=True)
            except Language.DoesNotExist:
                return Response(
                    {'error': 'Invalid language code'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 번역 데이터 업데이트
            updated_count = 0
            for key, value in translations.items():
                translation, created = Translation.objects.update_or_create(
                    key=key,
                    language=language,
                    defaults={'value': value, 'is_validated': True}
                )
                updated_count += 1
            
            logger.info(f"Bulk translation update: {updated_count} translations updated for {language_code}")
            
            return Response({
                'message': f'{updated_count} translations updated successfully',
                'language': language_code
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLanguagePreferenceView(APIView):
    """사용자 언어 설정 API"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """사용자 언어 설정 조회"""
        try:
            preference = UserLanguagePreference.objects.get(user=request.user)
            serializer = UserLanguagePreferenceSerializer(preference)
            return Response(serializer.data)
        except UserLanguagePreference.DoesNotExist:
            # 기본 설정 생성
            default_language = Language.objects.get(code='ko')
            preference = UserLanguagePreference.objects.create(
                user=request.user,
                language=default_language
            )
            serializer = UserLanguagePreferenceSerializer(preference)
            return Response(serializer.data)
    
    def post(self, request):
        """사용자 언어 설정 업데이트"""
        try:
            preference = UserLanguagePreference.objects.get(user=request.user)
            serializer = UserLanguagePreferenceUpdateSerializer(
                preference, data=request.data, partial=True
            )
        except UserLanguagePreference.DoesNotExist:
            # 새로운 설정 생성
            serializer = UserLanguagePreferenceUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            if hasattr(serializer, 'instance') and serializer.instance:
                serializer.save()
            else:
                # 새로운 설정 생성
                language_code = serializer.validated_data.get('language_code', 'ko')
                language = Language.objects.get(code=language_code)
                UserLanguagePreference.objects.create(
                    user=request.user,
                    language=language,
                    **{k: v for k, v in serializer.validated_data.items() if k != 'language_code'}
                )
            
            # 세션에 언어 설정 적용
            language_code = request.data.get('language_code')
            if language_code:
                activate(language_code)
                request.session['django_language'] = language_code
            
            return Response({'message': 'Language preference updated successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TranslationRequestViewSet(viewsets.ModelViewSet):
    """번역 요청 관리 API"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """사용자별 번역 요청 조회"""
        if self.request.user.is_staff:
            return TranslationRequest.objects.all()
        return TranslationRequest.objects.filter(requested_by=self.request.user)
    
    def get_serializer_class(self):
        """액션별 시리얼라이저 선택"""
        if self.action == 'create':
            return TranslationRequestCreateSerializer
        return TranslationRequestSerializer
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """번역 요청 승인 (관리자용)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        translation_request = self.get_object()
        translated_text = request.data.get('translated_text')
        
        if not translated_text:
            return Response(
                {'error': 'Translated text is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 번역 요청 완료 처리
        translation_request.translated_text = translated_text
        translation_request.status = 'completed'
        translation_request.assigned_to = request.user
        translation_request.save()
        
        # Translation 모델에 번역 데이터 저장
        Translation.objects.update_or_create(
            key=translation_request.key,
            language=translation_request.target_language,
            defaults={
                'value': translated_text,
                'category': translation_request.category,
                'context': translation_request.context,
                'is_validated': True
            }
        )
        
        logger.info(f"Translation request approved: {translation_request.key} -> {translation_request.target_language.code}")
        
        return Response({'message': 'Translation request approved and completed'})


class LanguageDetectionView(APIView):
    """언어 감지 API"""
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def post(self, request):
        """텍스트의 언어 감지"""
        text = request.data.get('text')
        if not text:
            return Response(
                {'error': 'Text is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        detected_language = LanguageDetectionService.detect_language(text)
        
        if detected_language:
            try:
                language = Language.objects.get(code=detected_language, is_active=True)
                serializer = LanguageSerializer(language)
                return Response({
                    'detected_language': serializer.data,
                    'confidence': 0.95  # 실제 구현에서는 감지 신뢰도 포함
                })
            except Language.DoesNotExist:
                pass
        
        return Response({
            'detected_language': None,
            'confidence': 0.0,
            'message': 'Could not detect language'
        })


class AutoTranslationView(APIView):
    """자동 번역 API"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """자동 번역 수행"""
        text = request.data.get('text')
        source_language = request.data.get('source_language', 'auto')
        target_language = request.data.get('target_language', 'ko')
        
        if not text:
            return Response(
                {'error': 'Text is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            translated_text = TranslationService.translate_text(
                text=text,
                source_language=source_language,
                target_language=target_language
            )
            
            return Response({
                'original_text': text,
                'translated_text': translated_text,
                'source_language': source_language,
                'target_language': target_language
            })
        
        except Exception as e:
            logger.error(f"Auto translation error: {str(e)}")
            return Response(
                {'error': 'Translation service unavailable'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
