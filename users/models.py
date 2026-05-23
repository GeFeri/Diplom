import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Студент'
        TEACHER = 'teacher', 'Преподаватель'
        MANAGER = 'manager', 'Менеджер'
        ADMIN   = 'admin',   'Администратор'

    class Tariff(models.TextChoices):
        FREE     = 'free',     'Бесплатный'
        BASIC    = 'basic',    'Базовый'
        STANDARD = 'standard', 'Стандартный'
        PREMIUM  = 'premium',  'Премиум'

    middle_name = models.CharField('Отчество', max_length=150, blank=True)
    role = models.CharField('Роль', max_length=20, choices=Role.choices, default=Role.STUDENT)
    tariff = models.CharField('Тариф', max_length=20, choices=Tariff.choices, default=Tariff.FREE)
    group = models.ForeignKey(
        'courses.StudentGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name='Группа',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def get_full_name(self):
        parts = [self.last_name, self.first_name, self.middle_name]
        full = ' '.join(p for p in parts if p)
        return full if full else self.username

    def is_teacher(self):
        return self.role == self.Role.TEACHER

    def is_student(self):
        return self.role == self.Role.STUDENT


class RegistrationToken(models.Model):
    token = models.UUIDField('Токен', default=uuid.uuid4, unique=True, editable=False)
    username = models.CharField('Логин студента', max_length=150, unique=True)
    last_name = models.CharField('Фамилия', max_length=150)
    first_name = models.CharField('Имя', max_length=150)
    middle_name = models.CharField('Отчество', max_length=150, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tokens',
        verbose_name='Создал',
    )
    is_used = models.BooleanField('Использован', default=False)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Ссылка для регистрации'
        verbose_name_plural = 'Ссылки для регистрации'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.last_name} {self.first_name} ({self.username})'
