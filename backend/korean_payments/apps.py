from django.apps import AppConfig


class KoreanPaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'korean_payments'
    verbose_name = '한국 결제 게이트웨이'

    def ready(self):
        """
        앱이 로드될 때 실행되는 초기화 코드
        """
        pass
