from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def teacher_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        role = request.user.role
        if role not in ('teacher', 'admin') and not request.user.is_superuser:
            messages.error(request, 'Доступ разрешён только преподавателям.')
            return redirect('courses:section_list')
        return view_func(request, *args, **kwargs)
    return wrapper


def manager_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        role = request.user.role
        if role not in ('manager', 'admin') and not request.user.is_superuser:
            messages.error(request, 'Доступ разрешён только менеджерам.')
            return redirect('courses:section_list')
        return view_func(request, *args, **kwargs)
    return wrapper
