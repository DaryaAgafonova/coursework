import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django.utils import timezone
from django.conf import settings
from .models import Mailing
from .services import send_mailing

logger = logging.getLogger(__name__)

def check_mailings():
    """
    Проверяет активные рассылки и отправляет их при необходимости
    """
    now = timezone.now()
    active_mailings = Mailing.objects.filter(
        status='started',
        start_time__lte=now,
        end_time__gte=now
    )
    
    for mailing in active_mailings:
        # Для однократных рассылок проверяем, что они еще не были отправлены
        if mailing.frequency == 'once' and mailing.logs.exists():
            continue
            
        # Для периодических рассылок проверяем, нужно ли отправлять сейчас
        if mailing.frequency == 'daily':
            send_mailing(mailing.id)
        elif mailing.frequency == 'weekly' and now.weekday() == 0:  # Понедельник
            send_mailing(mailing.id)
        elif mailing.frequency == 'monthly' and now.day == 1:  # Первый день месяца
            send_mailing(mailing.id)
            
    logger.info(f"Проверка рассылок завершена. Обработано {active_mailings.count()} активных рассылок.")

def start():
    """
    Запускает планировщик задач
    """
    try:
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        # Запускаем проверку рассылок каждый день в 8:00
        scheduler.add_job(
            check_mailings,
            trigger=CronTrigger(hour="8", minute="0"),
            id="check_mailings",
            max_instances=1,
            replace_existing=True,
        )
        
        # Также добавляем проверку каждый час для более частых рассылок
        scheduler.add_job(
            check_mailings,
            trigger=CronTrigger(minute="0"),  # Каждый час в :00 минут
            id="hourly_check_mailings",
            max_instances=1,
            replace_existing=True,
        )
        
        logger.info("Планировщик задач запущен.")
        scheduler.start()
    except Exception as e:
        logger.error(f"Ошибка при запуске планировщика задач: {str(e)}")
