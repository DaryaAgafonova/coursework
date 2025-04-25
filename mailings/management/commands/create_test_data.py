from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mailings.models import Client, Message, Mailing, UserProfile
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Создает тестовые данные для приложения рассылок'

    def handle(self, *args, **options):
        # Создаем тестового пользователя
        username = 'testuser'
        email = 'test@example.com'
        password = 'testpassword123'
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(self.style.WARNING(f'Пользователь {username} уже существует'))
        except User.DoesNotExist:
            user = User.objects.create_user(username=username, email=email, password=password)
            UserProfile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Создан пользователь {username}'))
        
        # Создаем тестовых клиентов
        clients = []
        for i in range(1, 11):
            client, created = Client.objects.get_or_create(
                email=f'client{i}@example.com',
                defaults={
                    'full_name': f'Тестовый Клиент {i}',
                    'comment': f'Комментарий для клиента {i}',
                    'owner': user
                }
            )
            if created:
                clients.append(client)
                self.stdout.write(self.style.SUCCESS(f'Создан клиент {client.full_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Клиент {client.full_name} уже существует'))
        
        # Создаем тестовые сообщения
        messages = []
        for i in range(1, 6):
            message, created = Message.objects.get_or_create(
                subject=f'Тестовое сообщение {i}',
                defaults={
                    'body': f'Это тестовое сообщение номер {i}. Оно содержит тестовый текст для рассылки.',
                    'owner': user
                }
            )
            if created:
                messages.append(message)
                self.stdout.write(self.style.SUCCESS(f'Создано сообщение "{message.subject}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Сообщение "{message.subject}" уже существует'))
        
        # Создаем тестовые рассылки
        frequencies = ['once', 'daily', 'weekly', 'monthly']
        statuses = ['created', 'started', 'completed']
        
        for i in range(1, 6):
            now = timezone.now()
            
            # Разные даты начала и окончания для разных рассылок
            if i % 3 == 0:
                # Рассылка в прошлом
                start_time = now - timezone.timedelta(days=10)
                end_time = now - timezone.timedelta(days=5)
            elif i % 3 == 1:
                # Активная рассылка
                start_time = now - timezone.timedelta(days=1)
                end_time = now + timezone.timedelta(days=10)
            else:
                # Будущая рассылка
                start_time = now + timezone.timedelta(days=5)
                end_time = now + timezone.timedelta(days=15)
            
            mailing, created = Mailing.objects.get_or_create(
                name=f'Тестовая рассылка {i}',
                defaults={
                    'start_time': start_time,
                    'end_time': end_time,
                    'frequency': random.choice(frequencies),
                    'status': random.choice(statuses),
                    'message': random.choice(messages),
                    'owner': user
                }
            )
            
            if created:
                # Добавляем случайных клиентов к рассылке
                selected_clients = random.sample(clients, min(len(clients), random.randint(3, 7)))
                mailing.clients.set(selected_clients)
                self.stdout.write(self.style.SUCCESS(f'Создана рассылка "{mailing.name}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Рассылка "{mailing.name}" уже существует'))
        
        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы!'))
