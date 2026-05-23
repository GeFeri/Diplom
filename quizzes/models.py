from django.conf import settings
from django.db import models

from courses.models import Lesson


class Quiz(models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE,
        related_name='quizzes', verbose_name='Урок',
    )
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    passing_score = models.PositiveIntegerField('Проходной балл (%)', default=60)
    time_limit = models.PositiveIntegerField(
        'Ограничение времени (мин)', default=0,
        help_text='0 — без ограничений',
    )
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'
        ordering = ['lesson', 'title']

    def __str__(self) -> str:
        return f'{self.title} ({self.lesson.title})'


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE,
        related_name='questions', verbose_name='Тест',
    )
    text = models.TextField('Текст вопроса')
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['order']

    def __str__(self) -> str:
        return f'Вопрос {self.order}: {self.text[:60]}'


class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        related_name='options', verbose_name='Вопрос',
    )
    text = models.CharField('Текст ответа', max_length=500)
    is_correct = models.BooleanField('Правильный', default=False)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'
        ordering = ['order']

    def __str__(self) -> str:
        return self.text


class QuizAttempt(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', 'В процессе'
        COMPLETED = 'completed', 'Завершён'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='quiz_attempts', verbose_name='Пользователь',
    )
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE,
        related_name='attempts', verbose_name='Тест',
    )
    status = models.CharField(
        'Статус', max_length=20,
        choices=Status.choices, default=Status.IN_PROGRESS,
    )
    score = models.FloatField('Балл (%)', null=True, blank=True)
    started_at = models.DateTimeField('Начат', auto_now_add=True)
    completed_at = models.DateTimeField('Завершён', null=True, blank=True)

    class Meta:
        verbose_name = 'Попытка прохождения теста'
        verbose_name_plural = 'Попытки прохождения тестов'
        ordering = ['-started_at']

    def __str__(self) -> str:
        return f'{self.user.username} — {self.quiz.title} ({self.get_status_display()})'

    def is_passed(self) -> bool:
        return self.score is not None and self.score >= self.quiz.passing_score


class UserAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt, on_delete=models.CASCADE,
        related_name='answers', verbose_name='Попытка',
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        related_name='user_answers', verbose_name='Вопрос',
    )
    selected_option = models.ForeignKey(
        AnswerOption, on_delete=models.CASCADE,
        verbose_name='Выбранный ответ',
    )

    class Meta:
        verbose_name = 'Ответ пользователя'
        verbose_name_plural = 'Ответы пользователей'
        unique_together = ('attempt', 'question')

    def __str__(self) -> str:
        return f'{self.attempt} — {self.question}'
