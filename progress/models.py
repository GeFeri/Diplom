from django.conf import settings
from django.db import models

from courses.models import Lesson


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
