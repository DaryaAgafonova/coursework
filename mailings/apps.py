from django.apps import AppConfig
import sys


class MailingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailings'
    verbose_name = 'Управление рассылками'

    def ready(self):
        if 'runserver' in sys.argv:
            from .scheduler import start
            pass
