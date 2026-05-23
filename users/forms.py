from django import forms
from django.contrib.auth.password_validation import validate_password

from users.models import User


class LoginForm(forms.Form):
    username = forms.CharField(label='Логин', max_length=150)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class CreateInviteForm(forms.Form):
    last_name  = forms.CharField(label='Фамилия',  max_length=150)
    first_name = forms.CharField(label='Имя',       max_length=150)
    middle_name = forms.CharField(label='Отчество', max_length=150, required=False)
    username   = forms.CharField(label='Логин',     max_length=150)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует.')
        from users.models import RegistrationToken
        if RegistrationToken.objects.filter(username=username, is_used=False).exists():
            raise forms.ValidationError('Активная ссылка для этого логина уже создана.')
        return username


class InviteRegistrationForm(forms.Form):
    password1 = forms.CharField(label='Пароль',                widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля',  widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Пароли не совпадают.')
        if p1:
            validate_password(p1)
        return cleaned


class StudentEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('tariff', 'group')
