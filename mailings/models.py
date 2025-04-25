from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Профиль {self.user.username}"


class Client(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    comment = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clients')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    class Meta:
        ordering = ['full_name']
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Message(models.Model):
    subject = models.CharField(max_length=200)
    body = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Mailing(models.Model):
    STATUS_CHOICES = (
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
        ('canceled', 'Отменена'),
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    FREQUENCY_CHOICES = (
        ('once', 'Один раз'),
        ('daily', 'Ежедневно'),
        ('weekly', 'Еженедельно'),
        ('monthly', 'Ежемесячно'),
    )
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='created')
    clients = models.ManyToManyField(Client, related_name='mailings')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='mailings')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mailings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Рассылка {self.id} ({self.get_status_display()})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
    
    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.status == 'started'


class MailingLog(models.Model):
    STATUS_CHOICES = (
        ('success', 'Успешно'),
        ('error', 'Ошибка'),
    )
    
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='logs')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    sent_at = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Лог {self.id} для рассылки {self.mailing.id}"

    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Лог рассылки'
        verbose_name_plural = 'Логи рассылок'
