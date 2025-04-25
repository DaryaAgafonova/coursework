from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Client, Message, Mailing, UserProfile


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 5}),
        }


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['name', 'start_time', 'end_time', 'frequency', 'clients', 'message']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'clients': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'company_name']
        labels = {
            'company_name': 'Компания',
        }


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
