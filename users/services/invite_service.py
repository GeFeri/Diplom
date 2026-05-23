from users.models import RegistrationToken, User


def create_invite(manager_user, data):
    token = RegistrationToken.objects.create(
        username=data['username'],
        last_name=data['last_name'],
        first_name=data['first_name'],
        middle_name=data.get('middle_name', ''),
        created_by=manager_user,
    )
    return token


def get_valid_token(token_str):
    try:
        return RegistrationToken.objects.get(token=token_str, is_used=False)
    except (RegistrationToken.DoesNotExist, ValueError):
        return None


def register_via_token(token, password):
    user = User.objects.create_user(
        username=token.username,
        password=password,
        first_name=token.first_name,
        last_name=token.last_name,
        middle_name=token.middle_name,
        role=User.Role.STUDENT,
    )
    token.is_used = True
    token.save(update_fields=['is_used'])
    return user
