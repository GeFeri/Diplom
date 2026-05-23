from django.contrib.auth import authenticate

from users.models import User


def register_user(form_data):
    user = User.objects.create_user(
        username=form_data['username'],
        email=form_data.get('email', ''),
        password=form_data['password1'],
        first_name=form_data.get('first_name', ''),
        last_name=form_data.get('last_name', ''),
        middle_name=form_data.get('middle_name', ''),
        role=User.Role.STUDENT,
    )
    return user


def authenticate_user(username, password):
    return authenticate(username=username, password=password)
