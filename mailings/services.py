import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Mailing, MailingLog, Client

logger = logging.getLogger(__name__)

def send_mailing(mailing_id):
    """
    Отправляет рассылку по указанному ID
    """
    try:
        mailing = Mailing.objects.get(id=mailing_id)
        
        # Проверяем, активна ли рассылка
        if not mailing.is_active():
            logger.info(f"Рассылка {mailing.id} не активна")
            return
        
        # Получаем всех клиентов для рассылки
        clients = mailing.clients.all()
        
        for client in clients:
            try:
                # Отправляем письмо
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                
                # Логируем успешную отправку
                MailingLog.objects.create(
                    mailing=mailing,
                    client=client,
                    status='success'
                )
                
                logger.info(f"Письмо успешно отправлено клиенту {client.email} для рассылки {mailing.id}")
                
            except Exception as e:
                # Логируем ошибку
                MailingLog.objects.create(
                    mailing=mailing,
                    client=client,
                    status='failed',
                    error_message=str(e)
                )
                
                logger.error(f"Ошибка при отправке письма клиенту {client.email} для рассылки {mailing.id}: {str(e)}")
        
        # Если рассылка однократная, помечаем её как завершенную
        if mailing.frequency == 'once':
            mailing.status = 'completed'
            mailing.save()
            
    except Mailing.DoesNotExist:
        logger.error(f"Рассылка с ID {mailing_id} не найдена")
    except Exception as e:
        logger.error(f"Ошибка при обработке рассылки {mailing_id}: {str(e)}")
