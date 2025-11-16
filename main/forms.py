# main/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

def validate_cyrillic(value):
    import re
    if not re.match(r'^[а-яёА-ЯЁ\s-]+$', value):
        raise ValidationError('ФИО может содержать только кириллические буквы, пробелы и дефисы.')

def validate_username(value):
    import re
    if not re.match(r'^[a-zA-Z-]+$', value):
        raise ValidationError('Логин может содержать только латинские буквы и дефис.')

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        label='ФИО',
        max_length=150,
        validators=[validate_cyrillic],
        help_text='Только кириллица, пробелы и дефисы.'
    )
    email = forms.EmailField(
        label='Email',
        max_length=254,
        help_text='Введите действительный email.'
    )
    username = forms.CharField(
        label='Логин',
        max_length=150,
        validators=[validate_username],
        help_text='Только латиница и дефис.'
    )
    agreement = forms.BooleanField(
        label='Согласие на обработку персональных данных',
        error_messages={
            'required': 'Вы должны согласиться с обработкой персональных данных.'
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user