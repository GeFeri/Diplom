from django.urls import path

from courses import views

app_name = 'courses'

urlpatterns = [
    # Публичные
    path('', views.section_list, name='section_list'),
    path('sections/<int:section_id>/', views.section_detail, name='section_detail'),
    path('lessons/<slug:slug>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/<slug:slug>/complete/', views.lesson_complete, name='lesson_complete'),

    # Выбор группы (студент)
    path('groups/', views.choose_group, name='choose_group'),

    # Преподаватель — дашборд
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),

    # Преподаватель — разделы
    path('teacher/sections/new/', views.section_create, name='section_create'),
    path('teacher/sections/<int:section_id>/edit/', views.section_edit, name='section_edit'),
    path('teacher/sections/<int:section_id>/delete/', views.section_delete, name='section_delete'),

    # Преподаватель — уроки
    path('teacher/sections/<int:section_id>/lessons/new/', views.lesson_create, name='lesson_create'),
    path('teacher/lessons/<int:lesson_id>/', views.lesson_manage, name='lesson_manage'),
    path('teacher/lessons/<int:lesson_id>/edit/', views.lesson_edit, name='lesson_edit'),
    path('teacher/lessons/<int:lesson_id>/delete/', views.lesson_delete, name='lesson_delete'),

    # Преподаватель — примеры кода
    path('teacher/lessons/<int:lesson_id>/examples/new/', views.example_create, name='example_create'),
    path('teacher/examples/<int:example_id>/edit/', views.example_edit, name='example_edit'),
    path('teacher/examples/<int:example_id>/delete/', views.example_delete, name='example_delete'),

    # Преподаватель — задания
    path('teacher/lessons/<int:lesson_id>/tasks/new/', views.task_create, name='task_create'),
    path('teacher/tasks/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('teacher/tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),

    # Практические работы студентов
    path('lessons/<slug:slug>/tasks/<int:task_id>/submit/', views.task_submit, name='task_submit'),
    path('teacher/lessons/<int:lesson_id>/submissions/', views.lesson_submissions, name='lesson_submissions'),
    path('teacher/submissions/<int:submission_id>/grade/', views.grade_submission_view, name='grade_submission'),

    # Менеджер — назначения преподавателей
    path('manager/assignments/', views.section_assignments, name='section_assignments'),

    # Менеджер — группы
    path('manager/groups/', views.group_list, name='group_list'),
    path('manager/groups/new/', views.group_create, name='group_create'),
    path('manager/groups/<int:group_id>/edit/', views.group_edit, name='group_edit'),
    path('manager/groups/<int:group_id>/delete/', views.group_delete, name='group_delete'),

    # Менеджер — панель и студенты
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/students/', views.manager_student_list, name='manager_student_list'),
    path('manager/students/<int:student_id>/edit/', views.manager_student_edit, name='manager_student_edit'),

    # Менеджер — ссылки для регистрации
    path('manager/invites/', views.invite_list, name='invite_list'),
    path('manager/invites/new/', views.invite_create, name='invite_create'),
    path('manager/invites/<int:invite_id>/delete/', views.invite_delete, name='invite_delete'),
]
