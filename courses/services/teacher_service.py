from django.shortcuts import get_object_or_404

from courses.models import Section, Lesson, CodeExample, PracticalTask, StudentGroup


def can_edit_section(user, section):
    if user.is_superuser or getattr(user, 'role', '') == 'admin':
        return True
    return section.teachers.filter(pk=user.pk).exists()


def create_section(teacher, data):
    section = Section.objects.create(**data)
    section.teachers.add(teacher)
    return section


def update_section(section, data):
    for field, value in data.items():
        setattr(section, field, value)
    section.save()
    return section


def delete_section(section_id):
    get_object_or_404(Section, pk=section_id).delete()


def create_lesson(section, data):
    return Lesson.objects.create(section=section, **data)


def update_lesson(lesson, data):
    for field, value in data.items():
        setattr(lesson, field, value)
    lesson.slug = ''  # сбросить, чтобы slug пересчитался в save()
    lesson.save()
    return lesson


def delete_lesson(lesson_id):
    get_object_or_404(Lesson, pk=lesson_id).delete()


def create_code_example(lesson, data):
    return CodeExample.objects.create(lesson=lesson, **data)


def update_code_example(example, data):
    for field, value in data.items():
        setattr(example, field, value)
    example.save()
    return example


def delete_code_example(example_id):
    get_object_or_404(CodeExample, pk=example_id).delete()


def create_practical_task(lesson, data):
    return PracticalTask.objects.create(lesson=lesson, **data)


def update_practical_task(task, data):
    for field, value in data.items():
        setattr(task, field, value)
    task.save()
    return task


def delete_practical_task(task_id):
    get_object_or_404(PracticalTask, pk=task_id).delete()


def get_dashboard_stats():
    from django.db.models import Count
    sections = Section.objects.annotate(lesson_count=Count('lessons')).order_by('order')
    return {
        'sections': sections,
        'total_sections': sections.count(),
        'total_lessons': Lesson.objects.count(),
    }


def get_all_groups():
    from django.db.models import Count
    return (
        StudentGroup.objects
        .annotate(student_count=Count('students'))
        .prefetch_related('sections')
        .order_by('name')
    )


def create_group(manager_user, data):
    sections = data.pop('sections', [])
    group = StudentGroup.objects.create(created_by=manager_user, **data)
    if sections:
        group.sections.set(sections)
    return group


def update_group(group, data):
    sections = data.pop('sections', None)
    for field, value in data.items():
        setattr(group, field, value)
    group.save()
    if sections is not None:
        group.sections.set(sections)
    return group


def delete_group(group_id):
    get_object_or_404(StudentGroup, pk=group_id).delete()
