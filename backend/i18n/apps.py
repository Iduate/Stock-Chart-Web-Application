from django.apps import AppConfig


class I18nConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'i18n'
    verbose_name = '다국어 지원'

    def ready(self):
        """
        앱이 로드될 때 실행되는 초기화 코드
        """
        pass
