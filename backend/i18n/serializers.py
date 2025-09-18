from rest_framework import serializers
from .models import Language, Translation, UserLanguagePreference, TranslationRequest


class LanguageSerializer(serializers.ModelSerializer):
    """언어 정보 시리얼라이저"""
    
    class Meta:
        model = Language
        fields = ['code', 'name', 'native_name', 'is_active', 'flag_icon', 'rtl']


class TranslationSerializer(serializers.ModelSerializer):
    """번역 시리얼라이저"""
    
    language_code = serializers.CharField(source='language.code', read_only=True)
    
    class Meta:
        model = Translation
        fields = ['key', 'language_code', 'value', 'category', 'context']


class TranslationBulkSerializer(serializers.Serializer):
    """대량 번역 요청 시리얼라이저"""
    
    language_code = serializers.CharField(max_length=10)
    translations = serializers.DictField(child=serializers.CharField())


class UserLanguagePreferenceSerializer(serializers.ModelSerializer):
    """사용자 언어 설정 시리얼라이저"""
    
    language_code = serializers.CharField(source='language.code', read_only=True)
    language_name = serializers.CharField(source='language.native_name', read_only=True)
    
    class Meta:
        model = UserLanguagePreference
        fields = ['language_code', 'language_name', 'timezone', 'date_format', 'number_format', 'currency']


class UserLanguagePreferenceUpdateSerializer(serializers.ModelSerializer):
    """사용자 언어 설정 업데이트 시리얼라이저"""
    
    language_code = serializers.CharField(write_only=True)
    
    class Meta:
        model = UserLanguagePreference
        fields = ['language_code', 'timezone', 'date_format', 'number_format', 'currency']
    
    def validate_language_code(self, value):
        """언어 코드 유효성 검사"""
        try:
            Language.objects.get(code=value, is_active=True)
        except Language.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive language code.")
        return value
    
    def update(self, instance, validated_data):
        """언어 설정 업데이트"""
        language_code = validated_data.pop('language_code', None)
        if language_code:
            instance.language = Language.objects.get(code=language_code)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class TranslationRequestSerializer(serializers.ModelSerializer):
    """번역 요청 시리얼라이저"""
    
    source_language_code = serializers.CharField(source='source_language.code', read_only=True)
    target_language_code = serializers.CharField(source='target_language.code', read_only=True)
    requested_by_username = serializers.CharField(source='requested_by.username', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True, allow_null=True)
    
    class Meta:
        model = TranslationRequest
        fields = [
            'id', 'key', 'source_language_code', 'target_language_code', 
            'source_text', 'translated_text', 'category', 'context', 
            'priority', 'status', 'requested_by_username', 'assigned_to_username',
            'due_date', 'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['requested_by_username', 'created_at', 'updated_at']


class TranslationRequestCreateSerializer(serializers.ModelSerializer):
    """번역 요청 생성 시리얼라이저"""
    
    source_language_code = serializers.CharField(write_only=True)
    target_language_code = serializers.CharField(write_only=True)
    
    class Meta:
        model = TranslationRequest
        fields = [
            'key', 'source_language_code', 'target_language_code', 
            'source_text', 'category', 'context', 'priority', 'due_date'
        ]
    
    def validate_source_language_code(self, value):
        """원본 언어 코드 유효성 검사"""
        try:
            Language.objects.get(code=value, is_active=True)
        except Language.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive source language code.")
        return value
    
    def validate_target_language_code(self, value):
        """대상 언어 코드 유효성 검사"""
        try:
            Language.objects.get(code=value, is_active=True)
        except Language.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive target language code.")
        return value
    
    def create(self, validated_data):
        """번역 요청 생성"""
        source_language_code = validated_data.pop('source_language_code')
        target_language_code = validated_data.pop('target_language_code')
        
        validated_data['source_language'] = Language.objects.get(code=source_language_code)
        validated_data['target_language'] = Language.objects.get(code=target_language_code)
        validated_data['requested_by'] = self.context['request'].user
        
        return super().create(validated_data)
