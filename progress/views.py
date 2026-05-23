from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from progress.services import progress_service


@login_required
def my_progress(request):
    data = progress_service.get_user_progress(request.user)
    return render(request, 'progress/my_progress.html', data)
