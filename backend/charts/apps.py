from django.apps import AppConfig


class ChartsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'charts'
    
    def ready(self):
        # Import signals when the app is ready
        import charts.signals
