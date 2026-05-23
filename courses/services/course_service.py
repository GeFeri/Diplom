from django.shortcuts import get_object_or_404

from courses.models import Section, Lesson, TARIFF_LEVEL


def _is_staff(user):
    if user.is_superuser:
        return True
    return getattr(user, 'role', '') in ('teacher', 'admin')


def get_sections_with_access(user):
    from progress.models import UserLessonProgress

    if _is_staff(user):
        sections = list(
            Section.objects.filter(is_published=True)
            .prefetch_related('lessons')
            .order_by('order')
        )
        for section in sections:
            section.is_unlocked = True
            published_lessons = [l for l in section.lessons.all() if l.is_published]
            section.completion_percent = 0
            section.completed_count = 0
            section.total_count = len(published_lessons)
        return sections

    if not user.group_id:
        return None

    completed_lesson_ids = set(
        UserLessonProgress.objects
        .filter(user=user, status=UserLessonProgress.Status.COMPLETED)
        .values_list('lesson_id', flat=True)
    )

    sections = list(
        user.group.sections.filter(is_published=True)
        .prefetch_related('lessons')
        .order_by('order')
    )

    prev_section_done = True
    for section in sections:
        section.is_unlocked = prev_section_done
        published_lessons = [l for l in section.lessons.all() if l.is_published]

        if published_lessons:
            done = sum(1 for l in published_lessons if l.pk in completed_lesson_ids)
            total = len(published_lessons)
            section.completion_percent = round(done / total * 100)
            section.completed_count = done
            section.total_count = total
        else:
            section.completion_percent = 0
            section.completed_count = 0
            section.total_count = 0

        prev_section_done = section.is_unlocked and section.completion_percent == 100

    return sections


def check_section_access(user, section):
    if _is_staff(user):
        return True

    if not user.group_id:
        return False

    if not user.group.sections.filter(pk=section.pk).exists():
        return False

    from progress.models import UserLessonProgress

    prev_sections = list(
        user.group.sections
        .filter(is_published=True, order__lt=section.order)
        .prefetch_related('lessons')
        .order_by('order')
    )

    if not prev_sections:
        return True

    completed_lesson_ids = set(
        UserLessonProgress.objects
        .filter(user=user, status=UserLessonProgress.Status.COMPLETED)
        .values_list('lesson_id', flat=True)
    )

    for prev in prev_sections:
        lessons = [l for l in prev.lessons.all() if l.is_published]
        if lessons and not all(l.pk in completed_lesson_ids for l in lessons):
            return False

    return True


def get_available_groups(user):
    from courses.models import StudentGroup

    user_tariff_level = TARIFF_LEVEL.get(getattr(user, 'tariff', 'free'), 0)
    groups = list(StudentGroup.objects.prefetch_related('sections'))

    for group in groups:
        group_level = TARIFF_LEVEL.get(group.required_tariff, 0)
        group.is_eligible = group_level <= user_tariff_level

    return groups


def get_published_sections():
    return Section.objects.filter(is_published=True).prefetch_related('lessons')


def get_section_with_lessons(section_id):
    return get_object_or_404(
        Section.objects.prefetch_related(
            'lessons__code_examples',
            'lessons__practical_tasks',
        ),
        pk=section_id,
        is_published=True,
    )


def get_lesson_full_data(slug):
    return get_object_or_404(
        Lesson.objects
        .select_related('section')
        .prefetch_related('code_examples', 'practical_tasks', 'quizzes'),
        slug=slug,
        is_published=True,
    )
