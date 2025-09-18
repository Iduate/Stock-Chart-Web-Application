from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from .models import Language, Translation, UserLanguagePreference, TranslationRequest


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('native_name', 'code', 'name', 'flag_display', 'is_active', 'rtl', 'translation_count')
    list_filter = ('is_active', 'rtl')
    search_fields = ('name', 'native_name', 'code')
    list_editable = ('is_active',)
    readonly_fields = ('translation_count', 'created_at')
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('code', 'name', 'native_name', 'flag_icon')
        }),
        ('설정', {
            'fields': ('is_active', 'rtl')
        }),
        ('통계', {
            'fields': ('translation_count',),
            'classes': ('collapse',)
        }),
        ('시간 정보', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def flag_display(self, obj):
        if obj.flag_icon:
            return format_html('<span style="font-size: 20px;">{}</span>', obj.flag_icon)
        return '-'
    flag_display.short_description = '국기'
    
    def translation_count(self, obj):
        count = Translation.objects.filter(language=obj).count()
        url = reverse('admin:i18n_translation_changelist') + f'?language__id__exact={obj.id}'
        return format_html('<a href="{}">{} 개</a>', url, count)
    translation_count.short_description = '번역 수'


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('key', 'language', 'value_preview', 'category', 'is_validated', 'updated_at')
    list_filter = ('language', 'category', 'is_validated', 'created_at')
    search_fields = ('key', 'value', 'context')
    list_editable = ('is_validated',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('key', 'language', 'category')
        }),
        ('번역 내용', {
            'fields': ('value', 'context')
        }),
        ('상태', {
            'fields': ('is_validated',)
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['validate_translations', 'invalidate_translations', 'export_translations']
    
    def value_preview(self, obj):
        if len(obj.value) > 50:
            return obj.value[:50] + '...'
        return obj.value
    value_preview.short_description = '번역값'
    
    def validate_translations(self, request, queryset):
        updated = queryset.update(is_validated=True)
        self.message_user(request, f'{updated}개 번역이 검증되었습니다.')
    validate_translations.short_description = '선택된 번역 검증'
    
    def invalidate_translations(self, request, queryset):
        updated = queryset.update(is_validated=False)
        self.message_user(request, f'{updated}개 번역이 미검증으로 변경되었습니다.')
    invalidate_translations.short_description = '선택된 번역 미검증으로 변경'
    
    def export_translations(self, request, queryset):
        # 번역 데이터 내보내기 (CSV, JSON 등)
        # 실제 구현에서는 파일 다운로드 기능 추가
        self.message_user(request, f'{queryset.count()}개 번역 데이터를 내보냈습니다.')
    export_translations.short_description = '선택된 번역 내보내기'


@admin.register(UserLanguagePreference)
class UserLanguagePreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'timezone', 'currency', 'created_at')
    list_filter = ('language', 'timezone', 'currency', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('사용자 정보', {
            'fields': ('user', 'language')
        }),
        ('지역 설정', {
            'fields': ('timezone', 'date_format', 'number_format', 'currency')
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TranslationRequest)
class TranslationRequestAdmin(admin.ModelAdmin):
    list_display = ('key', 'source_language', 'target_language', 'status_badge', 'priority_badge', 'requested_by', 'assigned_to', 'due_date')
    list_filter = ('status', 'priority', 'source_language', 'target_language', 'category', 'created_at')
    search_fields = ('key', 'source_text', 'translated_text', 'requested_by__username')
    readonly_fields = ('requested_by', 'created_at', 'updated_at', 'completed_at')
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('key', 'source_language', 'target_language', 'category')
        }),
        ('번역 내용', {
            'fields': ('source_text', 'translated_text', 'context')
        }),
        ('상태 및 우선순위', {
            'fields': ('status', 'priority', 'assigned_to', 'due_date')
        }),
        ('요청자 정보', {
            'fields': ('requested_by',),
            'classes': ('collapse',)
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['assign_to_me', 'mark_completed', 'mark_in_progress']
    
    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',
            'in_progress': '#3b82f6',
            'completed': '#10b981',
            'rejected': '#ef4444'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_badge.short_description = '상태'
    
    def priority_badge(self, obj):
        colors = {
            'low': '#6b7280',
            'medium': '#f59e0b',
            'high': '#ef4444',
            'urgent': '#dc2626'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            colors.get(obj.priority, '#6b7280'),
            obj.get_priority_display()
        )
    priority_badge.short_description = '우선순위'
    
    def assign_to_me(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            assigned_to=request.user, 
            status='in_progress'
        )
        self.message_user(request, f'{updated}개 번역 요청이 본인에게 할당되었습니다.')
    assign_to_me.short_description = '선택된 요청을 나에게 할당'
    
    def mark_completed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status='completed',
            completed_at=timezone.now()
        )
        self.message_user(request, f'{updated}개 번역 요청이 완료 처리되었습니다.')
    mark_completed.short_description = '선택된 요청 완료 처리'
    
    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated}개 번역 요청이 진행중으로 변경되었습니다.')
    mark_in_progress.short_description = '선택된 요청 진행중으로 변경'


# Admin 사이트 커스터마이징
admin.site.site_header = "StockChart 다국어 관리"
admin.site.site_title = "StockChart I18N Admin"
admin.site.index_title = "다국어 지원 시스템 관리"
