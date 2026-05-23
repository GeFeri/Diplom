from django.conf import settings
from django.shortcuts import redirect


OPEN_URLS = (
    settings.LOGIN_URL,
    '/users/register/',
    '/admin/',
)


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            current_path = request.path_info
            is_open = any(current_path.startswith(url) for url in OPEN_URLS)
            if not is_open:
                return redirect(f'{settings.LOGIN_URL}?next={current_path}')
        return self.get_response(request)
