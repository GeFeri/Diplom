from django.utils import timezone

from courses.models import Lesson
from progress.models import UserLessonProgress, TaskSubmission


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


def submit_task(user, task, file):
    sub, _ = TaskSubmission.objects.update_or_create(
        task=task, user=user,
        defaults={
            'file': file,
            'status': TaskSubmission.Status.PENDING,
            'comment': '',
            'reviewed_by': None,
            'reviewed_at': None,
        },
    )
    return sub


def grade_submission(submission, teacher, status, comment):
    submission.status = status
    submission.comment = comment
    submission.reviewed_by = teacher
    submission.reviewed_at = timezone.now()
    submission.save(update_fields=['status', 'comment', 'reviewed_by', 'reviewed_at'])


def all_tasks_accepted(user, lesson):
    tasks = lesson.practical_tasks.all()
    if not tasks.exists():
        return True
    accepted_count = TaskSubmission.objects.filter(
        task__in=tasks, user=user, status=TaskSubmission.Status.ACCEPTED,
    ).count()
    return accepted_count == tasks.count()


def get_user_progress(user):
    from courses.models import Section
    from courses.services.course_service import _is_staff, get_sections_with_access

    if _is_staff(user):
        raw = list(
            Section.objects.filter(is_published=True)
            .prefetch_related('lessons')
            .order_by('order')
        )
        for s in raw:
            s.is_unlocked = True
        sections = raw
    elif not user.group_id:
        return {'sections_data': [], 'total': 0, 'completed': 0, 'percent': 0}
    else:
        sections = get_sections_with_access(user) or []

    existing = {
        p.lesson_id: p
        for p in UserLessonProgress.objects.filter(user=user)
    }

    sections_data = []
    total = 0
    completed = 0

    for section in sections:
        published = sorted(
            [l for l in section.lessons.all() if l.is_published],
            key=lambda l: l.order,
        )
        lesson_rows = []
        for lesson in published:
            total += 1
            prog = existing.get(lesson.pk)
            if prog and prog.status == UserLessonProgress.Status.COMPLETED:
                completed += 1
            lesson_rows.append({
                'lesson': lesson,
                'status': prog.status if prog else UserLessonProgress.Status.NOT_STARTED,
                'status_display': prog.get_status_display() if prog else 'Не начат',
                'score': prog.score if prog else None,
                'completed_at': prog.completed_at if prog else None,
                'is_locked': not section.is_unlocked,
            })

        if lesson_rows:
            sections_data.append({
                'section': section,
                'is_unlocked': section.is_unlocked,
                'lessons': lesson_rows,
            })

    percent = round(completed / total * 100) if total > 0 else 0
    return {
        'sections_data': sections_data,
        'total': total,
        'completed': completed,
        'percent': percent,
    }
