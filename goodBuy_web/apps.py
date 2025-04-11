from django.apps import AppConfig

class GoodBuyWebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'goodBuy_web'

    def ready(self):
        import goodBuy_web.signals