from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.views import (
    LoginView, LogoutView, 
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserProfileForm, UserUpdateForm
from users.models import UserProfile
import pdb


class UserRegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'mailings/users/register.html'
    success_url = reverse_lazy('login')  # We'll use this only if get_success_url isn't defined
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Вы успешно зарегистрированы!')
        return redirect(self.get_success_url())  # Call get_success_url

    def get_success_url(self):
        return reverse('login')  # Explicitly return the URL by name

    def form_invalid(self, form):
        messages.error(self.request, 'Ошибка при регистрации. Пожалуйста, исправьте ошибки ниже.')
        return self.render_to_response(self.get_context_data(form=form))


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
