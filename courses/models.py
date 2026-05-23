from django.conf import settings
from django.db import models


TARIFF_CHOICES = [
    ('free',     'Бесплатный'),
    ('basic',    'Базовый'),
    ('standard', 'Стандартный'),
    ('premium',  'Премиум'),
]

TARIFF_LEVEL = {
    'free':     0,
    'basic':    1,
    'standard': 2,
    'premium':  3,
}


class Section(models.Model):
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_published = models.BooleanField('Опубликован', default=False)
    teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='assigned_sections',
        verbose_name='Прикреплённые преподаватели',
    )
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'
        ordering = ['order']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Раздел',
    )
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Слаг', max_length=200, unique=True, blank=True)
    content = models.TextField('Содержание')
    order = models.PositiveIntegerField('Порядок', default=0)
    is_published = models.BooleanField('Опубликован', default=False)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['order']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = f'{self.section.order}-{self.order}'
            slug = base_slug
            counter = 1
            while Lesson.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class CodeExample(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='code_examples',
        verbose_name='Урок',
    )
    title = models.CharField('Название', max_length=200)
    code = models.TextField('Код')
    explanation = models.TextField('Объяснение', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Пример кода'
        verbose_name_plural = 'Примеры кода'
        ordering = ['order']

    def __str__(self):
        return self.title


class PracticalTask(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='practical_tasks',
        verbose_name='Урок',
    )
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание задания')
    hint = models.TextField('Подсказка', blank=True)
    solution = models.TextField('Решение', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Практическое задание'
        verbose_name_plural = 'Практические задания'
        ordering = ['order']

    def __str__(self):
        return self.title


class StudentGroup(models.Model):
    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    required_tariff = models.CharField(
        'Минимальный тариф',
        max_length=20,
        choices=TARIFF_CHOICES,
        default='free',
    )
    sections = models.ManyToManyField(
        Section,
        blank=True,
        related_name='groups',
        verbose_name='Разделы',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_groups',
        verbose_name='Создал',
    )
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['name']

    def __str__(self):
        return self.name
