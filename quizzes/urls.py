from django.urls import path

from quizzes import views

app_name = 'quizzes'

urlpatterns = [
    path('<int:quiz_id>/start/', views.quiz_start, name='quiz_start'),
    path('attempt/<int:attempt_id>/', views.quiz_attempt, name='quiz_attempt'),
    path('result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),

    path('teacher/lessons/<int:lesson_id>/quiz/new/', views.quiz_create, name='quiz_create'),
    path('teacher/quiz/<int:quiz_id>/edit/', views.quiz_edit, name='quiz_edit'),
    path('teacher/quiz/<int:quiz_id>/delete/', views.quiz_delete, name='quiz_delete'),

    path('teacher/quiz/<int:quiz_id>/questions/new/', views.question_create, name='question_create'),
    path('teacher/questions/<int:question_id>/edit/', views.question_edit, name='question_edit'),
    path('teacher/questions/<int:question_id>/delete/', views.question_delete, name='question_delete'),
]
