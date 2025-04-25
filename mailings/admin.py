from django.contrib import admin
from .models import Client, Message, Mailing, MailingLog, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_verified', 'phone', 'company_name']
    search_fields = ['user__username', 'user__email', 'phone', 'company_name']
    list_filter = ['is_verified']

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'owner', 'created_at']
    search_fields = ['email', 'full_name']
    list_filter = ['owner', 'created_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'owner', 'created_at']
    search_fields = ['subject', 'body']
    list_filter = ['owner', 'created_at']

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'frequency', 'status', 'owner']
    search_fields = ['name']
    list_filter = ['status', 'frequency', 'owner', 'created_at']
    filter_horizontal = ['clients']

@admin.register(MailingLog)
class MailingLogAdmin(admin.ModelAdmin):
    list_display = ['mailing', 'client', 'status', 'sent_at']
    search_fields = ['mailing__name', 'client__email']
    list_filter = ['status', 'sent_at']
