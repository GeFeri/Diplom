from django.utils import timezone

from courses.models import Lesson
from progress.models import UserLessonProgress


def mark_lesson_started(user, lesson):
    progress, created = UserLessonProgress.objects.get_or_create(
        user=user,
        lesson=lesson,
        defaults={
            'status': UserLessonProgress.Status.IN_PROGRESS,
            'started_at': timezone.now(),
        },
    )
    if not created and progress.status == UserLessonProgress.Status.NOT_STARTED:
        progress.status = UserLessonProgress.Status.IN_PROGRESS
        progress.started_at = timezone.now()
        progress.save(update_fields=['status', 'started_at'])
    return progress


def mark_lesson_completed(user, lesson, score=None, time_spent=0):
    progress, _ = UserLessonProgress.objects.get_or_create(user=user, lesson=lesson)
    progress.status = UserLessonProgress.Status.COMPLETED
    progress.score = score
    progress.time_spent = time_spent
    progress.completed_at = timezone.now()
    if not progress.started_at:
        progress.started_at = timezone.now()
    progress.save()
    return progress


def get_user_progress(user):
    progress_list = (
        UserLessonProgress.objects
        .filter(user=user)
        .select_related('lesson__section')
        .order_by('lesson__section__order', 'lesson__order')
    )
    total = progress_list.count()
    completed = progress_list.filter(status=UserLessonProgress.Status.COMPLETED).count()
    percent = round(completed / total * 100) if total > 0 else 0
    return {
        'progress_list': progress_list,
        'total': total,
        'completed': completed,
        'percent': percent,
    }
