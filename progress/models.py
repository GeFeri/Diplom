from django.conf import settings
from django.db import models

from courses.models import Lesson


class TaskSubmission(models.Model):
    class Status(models.TextChoices):
        PENDING  = 'pending',  'На проверке'
        ACCEPTED = 'accepted', 'Зачтено'
        REJECTED = 'rejected', 'На доработку'

    task = models.ForeignKey(
        'courses.PracticalTask', on_delete=models.CASCADE,
        related_name='submissions', verbose_name='Задание',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='task_submissions', verbose_name='Студент',
    )
    file = models.FileField('Файл', upload_to='submissions/%Y/%m/')
    status = models.CharField(
        'Статус', max_length=20,
        choices=Status.choices, default=Status.PENDING,
    )
    comment = models.TextField('Комментарий преподавателя', blank=True)
    submitted_at = models.DateTimeField('Дата отправки', auto_now=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reviewed_submissions', verbose_name='Проверил',
    )
    reviewed_at = models.DateTimeField('Дата проверки', null=True, blank=True)

    class Meta:
        unique_together = ('task', 'user')
        verbose_name = 'Работа студента'
        verbose_name_plural = 'Работы студентов'
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.user.username} — {self.task.title} ({self.get_status_display()})'


class UserLessonProgress(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', 'Не начат'
        IN_PROGRESS = 'in_progress', 'В процессе'
        COMPLETED = 'completed', 'Завершён'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='lesson_progress', verbose_name='Пользователь',
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE,
        related_name='user_progress', verbose_name='Урок',
    )
    status = models.CharField(
        'Статус', max_length=20,
        choices=Status.choices, default=Status.NOT_STARTED,
    )
    score = models.FloatField('Балл', null=True, blank=True)
    time_spent = models.PositiveIntegerField('Потрачено времени (сек)', default=0)
    started_at = models.DateTimeField('Начат', null=True, blank=True)
    completed_at = models.DateTimeField('Завершён', null=True, blank=True)

    class Meta:
        verbose_name = 'Прогресс по уроку'
        verbose_name_plural = 'Прогресс по урокам'
        unique_together = ('user', 'lesson')
        ordering = ['lesson__section__order', 'lesson__order']

    def __str__(self) -> str:
        return f'{self.user.username} — {self.lesson.title} ({self.get_status_display()})'
