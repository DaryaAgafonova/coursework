from django.core.management.base import BaseCommand
from mailings.scheduler import start
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Запускает планировщик задач для рассылок'

    def handle(self, *args, **options):
        self.stdout.write('Запуск планировщика задач...')
        start()
        self.stdout.write(self.style.SUCCESS('Планировщик задач успешно запущен!'))
        
        try:
            # Держим процесс запущенным
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Планировщик задач остановлен.'))
