from django.urls import path

from users import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('register/<uuid:token>/', views.register_via_token_view, name='register_via_token'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]
