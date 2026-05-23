from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from users.forms import LoginForm, CreateInviteForm, InviteRegistrationForm
from users.services import user_service, invite_service


def register_view(request):
    messages.error(request, 'Регистрация доступна только по индивидуальной ссылке.')
    return redirect('users:login')


def register_via_token_view(request, token):
    invite = invite_service.get_valid_token(str(token))
    if invite is None:
        messages.error(request, 'Ссылка недействительна или уже была использована.')
        return redirect('users:login')

    if request.method == 'POST':
        form = InviteRegistrationForm(request.POST)
        if form.is_valid():
            user = invite_service.register_via_token(invite, form.cleaned_data['password1'])
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.get_full_name()}!')
            return redirect('courses:section_list')
    else:
        form = InviteRegistrationForm()

    return render(request, 'users/register_via_token.html', {
        'form': form,
        'invite': invite,
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('courses:section_list')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = user_service.authenticate_user(username, password)
            if user:
                login(request, user)
                next_url = request.GET.get('next', 'courses:section_list')
                return redirect(next_url)
            messages.error(request, 'Неверный логин или пароль.')
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('users:login')


@login_required
def profile_view(request):
    return render(request, 'users/profile.html')
