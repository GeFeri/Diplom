from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('courses.urls')),
    path('users/', include('users.urls')),
    path('quizzes/', include('quizzes.urls')),
    path('progress/', include('progress.urls')),
]
