from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from mailings.models import UserProfile


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
