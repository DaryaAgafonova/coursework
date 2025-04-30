from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth.views import (
    LoginView, LogoutView, 
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Client, Message, Mailing, MailingLog
from users.models import UserProfile
from .forms import ClientForm, MessageForm, MailingForm, UserRegisterForm, UserProfileForm, UserUpdateForm
from .services import send_mailing


class HomeView(TemplateView):
    template_name = 'mailings/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['total_clients'] = Client.objects.filter(owner=self.request.user).count()
            context['total_messages'] = Message.objects.filter(owner=self.request.user).count()
            context['total_mailings'] = Mailing.objects.filter(owner=self.request.user).count()
            context['active_mailings'] = Mailing.objects.filter(
                owner=self.request.user, 
                status='started',
                start_time__lte=timezone.now(),
                end_time__gte=timezone.now()
            ).count()
        return context


class UserRegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'mailings/users/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        UserProfile.objects.create(user=self.object)
        messages.success(self.request, 'Аккаунт успешно создан! Теперь вы можете войти.')
        return response


class UserLoginView(LoginView):
    template_name = 'mailings/users/login.html'
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    next_page = 'login'


class UserPasswordResetView(PasswordResetView):
    template_name = 'mailings/users/password_reset.html'
    email_template_name = 'mailings/users/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')


class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'mailings/users/password_reset_done.html'


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'mailings/users/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'mailings/users/password_reset_complete.html'


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'mailings/users/list.html'
    context_object_name = 'users'
    
    def test_func(self):
        return self.request.user.is_staff


class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    template_name = 'mailings/users/detail.html'
    context_object_name = 'user_profile'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.pk == self.kwargs.get('pk')


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'mailings/users/form.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy('user_list')
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.pk == self.kwargs.get('pk')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['profile_form'] = UserProfileForm(self.request.POST, instance=self.object.profile)
        else:
            context['profile_form'] = UserProfileForm(instance=self.object.profile)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        profile_form = context['profile_form']
        if profile_form.is_valid():
            profile_form.save()
        return super().form_valid(form)


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailings/clients/list.html'
    context_object_name = 'clients'
    
    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ClientDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Client
    template_name = 'mailings/clients/detail.html'
    context_object_name = 'client'
    
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailings/clients/form.html'
    success_url = reverse_lazy('client_list')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Клиент успешно создан!')
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailings/clients/form.html'
    success_url = reverse_lazy('client_list')
    
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Клиент успешно обновлен!')
        return super().form_valid(form)


class ClientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Client
    template_name = 'mailings/clients/confirm_delete.html'
    success_url = reverse_lazy('client_list')
    
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Клиент успешно удален!')
        return super().delete(request, *args, **kwargs)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailings/messages/list.html'
    context_object_name = 'messages'
    
    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Message
    template_name = 'mailings/messages/detail.html'
    context_object_name = 'message'
    
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/messages/form.html'
    success_url = reverse_lazy('message_list')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Сообщение успешно создано!')
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/messages/form.html'
    success_url = reverse_lazy('message_list')
    
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Сообщение успешно обновлено!')
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Message
    template_name = 'mailings/messages/confirm_delete.html'
    success_url = reverse_lazy('message_list')
    
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Сообщение успешно удалено!')
        return super().delete(request, *args, **kwargs)


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailings/mailings/list.html'
    context_object_name = 'mailings'
    
    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class MailingDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Mailing
    template_name = 'mailings/mailings/detail.html'
    context_object_name = 'mailing'
    
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['logs'] = MailingLog.objects.filter(mailing=self.object)
        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailings/form.html'
    success_url = reverse_lazy('mailing_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['clients'].queryset = Client.objects.filter(owner=self.request.user)
        form.fields['message'].queryset = Message.objects.filter(owner=self.request.user)
        return form
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Рассылка успешно создана!')
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailings/form.html'
    success_url = reverse_lazy('mailing_list')
    
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['clients'].queryset = Client.objects.filter(owner=self.request.user)
        form.fields['message'].queryset = Message.objects.filter(owner=self.request.user)
        return form
    
    def form_valid(self, form):
        messages.success(self.request, 'Рассылка успешно обновлена!')
        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Mailing
    template_name = 'mailings/mailings/confirm_delete.html'
    success_url = reverse_lazy('mailing_list')
    
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Рассылка успешно удалена!')
        return super().delete(request, *args, **kwargs)


class MailingStartView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        mailing = get_object_or_404(Mailing, pk=self.kwargs['pk'])
        return mailing.owner == self.request.user
    
    def post(self, request, *args, **kwargs):
        mailing = get_object_or_404(Mailing, pk=kwargs['pk'])
        if mailing.status != 'started':
            mailing.status = 'started'
            mailing.save()
            messages.success(request, 'Рассылка запущена!')
            
            if mailing.frequency == 'once' and mailing.start_time <= timezone.now():
                send_mailing(mailing.id)
        
        return redirect('mailing_detail', pk=mailing.pk)


class MailingStopView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        mailing = get_object_or_404(Mailing, pk=self.kwargs['pk'])
        return mailing.owner == self.request.user
    
    def post(self, request, *args, **kwargs):
        mailing = get_object_or_404(Mailing, pk=kwargs['pk'])
        if mailing.status == 'started':
            mailing.status = 'completed'
            mailing.save()
            messages.success(request, 'Рассылка остановлена!')
        
        return redirect('mailing_detail', pk=mailing.pk)


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'mailings/statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Общая статистика
        context['total_mailings'] = Mailing.objects.filter(owner=user).count()
        context['active_mailings'] = Mailing.objects.filter(
            owner=user, 
            status='started',
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now()
        ).count()
        context['total_clients'] = Client.objects.filter(owner=user).count()
        context['total_messages'] = Message.objects.filter(owner=user).count()
        
        # Статистика по рассылкам
        context['mailings_by_status'] = Mailing.objects.filter(owner=user).values('status').annotate(count=Count('id'))
        context['mailings_by_frequency'] = Mailing.objects.filter(owner=user).values('frequency').annotate(count=Count('id'))
        
        # Статистика по логам
        context['logs_by_status'] = MailingLog.objects.filter(mailing__owner=user).values('status').annotate(count=Count('id'))
        
        # Статистика по времени
        today = timezone.now().date()
        context['logs_today'] = MailingLog.objects.filter(mailing__owner=user, sent_at__date=today).count()
        context['logs_this_week'] = MailingLog.objects.filter(
            mailing__owner=user, 
            sent_at__date__gte=today - timezone.timedelta(days=7)
        ).count()
        context['logs_this_month'] = MailingLog.objects.filter(
            mailing__owner=user, 
            sent_at__date__gte=today - timezone.timedelta(days=30)
        ).count()
        
        return context
