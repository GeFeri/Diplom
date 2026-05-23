from django.urls import path

from progress import views

app_name = 'progress'

urlpatterns = [
    path('my/', views.my_progress, name='my_progress'),
]
