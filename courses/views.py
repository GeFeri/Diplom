from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from courses.models import Section, Lesson, CodeExample, PracticalTask, StudentGroup, TARIFF_LEVEL
from courses.services import course_service, teacher_service
from courses.forms import SectionForm, LessonForm, CodeExampleForm, PracticalTaskForm, StudentGroupForm
from progress.models import UserLessonProgress
from progress.services import progress_service
from quizzes.services.quiz_service import all_quizzes_passed, get_quiz_statuses
from users.decorators import teacher_required, manager_required
from users.forms import CreateInviteForm, StudentEditForm
from users.models import RegistrationToken
from users.services import invite_service


def section_list(request):
    user = request.user
    is_staff = user.is_superuser or getattr(user, 'role', '') in ('teacher', 'admin')
    if not is_staff and not user.group_id:
        return redirect('courses:choose_group')
    sections = course_service.get_sections_with_access(user)
    return render(request, 'courses/section_list.html', {'sections': sections})


def section_detail(request, section_id):
    section = course_service.get_section_with_lessons(section_id)
    if not course_service.check_section_access(request.user, section):
        messages.error(request, 'Этот раздел пока закрыт. Завершите предыдущий раздел на 100%.')
        return redirect('courses:section_list')
    completed_ids = set(
        UserLessonProgress.objects
        .filter(user=request.user, status=UserLessonProgress.Status.COMPLETED)
        .values_list('lesson_id', flat=True)
    )
    return render(request, 'courses/section_detail.html', {
        'section': section,
        'completed_ids': completed_ids,
    })


def lesson_detail(request, slug):
    lesson = course_service.get_lesson_full_data(slug)
    if not course_service.check_section_access(request.user, lesson.section):
        messages.error(request, 'Этот урок пока закрыт. Завершите предыдущий раздел на 100%.')
        return redirect('courses:section_list')

    progress_service.mark_lesson_started(request.user, lesson)

    lesson_progress = UserLessonProgress.objects.filter(
        user=request.user, lesson=lesson,
    ).first()
    is_completed = lesson_progress and lesson_progress.status == UserLessonProgress.Status.COMPLETED
    quizzes_ok = all_quizzes_passed(request.user, lesson)
    passed_quiz_ids = {qid for qid, ok in get_quiz_statuses(request.user, lesson).items() if ok}

    return render(request, 'courses/lesson_detail.html', {
        'lesson': lesson,
        'is_completed': is_completed,
        'quizzes_ok': quizzes_ok,
        'passed_quiz_ids': passed_quiz_ids,
    })


@login_required
def lesson_complete(request, slug):
    if request.method != 'POST':
        return redirect('courses:lesson_detail', slug=slug)
    lesson = get_object_or_404(Lesson, slug=slug, is_published=True)
    if not course_service.check_section_access(request.user, lesson.section):
        return redirect('courses:section_list')
    if not all_quizzes_passed(request.user, lesson):
        messages.error(request, 'Сначала пройдите все тесты урока на проходной балл.')
        return redirect('courses:lesson_detail', slug=slug)
    progress_service.mark_lesson_completed(request.user, lesson)
    messages.success(request, f'Урок «{lesson.title}» отмечен как пройденный.')
    return redirect('courses:lesson_detail', slug=slug)


@login_required
def choose_group(request):
    groups = course_service.get_available_groups(request.user)
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        group = get_object_or_404(StudentGroup, pk=group_id)
        user_level = TARIFF_LEVEL.get(request.user.tariff, 0)
        group_level = TARIFF_LEVEL.get(group.required_tariff, 0)
        if user_level >= group_level:
            request.user.group = group
            request.user.save(update_fields=['group'])
            messages.success(request, f'Вы вступили в группу «{group.name}».')
            return redirect('courses:section_list')
        messages.error(request, 'Ваш тариф не позволяет вступить в эту группу.')
    return render(request, 'courses/choose_group.html', {'groups': groups})


@teacher_required
def teacher_dashboard(request):
    stats = teacher_service.get_dashboard_stats()
    editable_ids = {
        s.pk for s in stats['sections']
        if teacher_service.can_edit_section(request.user, s)
    }
    return render(request, 'teacher/dashboard.html', {**stats, 'editable_ids': editable_ids})


@teacher_required
def section_create(request):
    form = SectionForm(request.POST or None)
    if form.is_valid():
        teacher_service.create_section(request.user, form.cleaned_data)
        messages.success(request, 'Раздел создан.')
        return redirect('courses:teacher_dashboard')
    return render(request, 'courses/teacher/section_form.html', {'form': form, 'title': 'Новый раздел'})


@teacher_required
def section_edit(request, section_id):
    section = get_object_or_404(Section, pk=section_id)
    if not teacher_service.can_edit_section(request.user, section):
        messages.error(request, 'Вы не прикреплены к этому разделу.')
        return redirect('courses:teacher_dashboard')
    form = SectionForm(request.POST or None, instance=section)
    if form.is_valid():
        teacher_service.update_section(section, form.cleaned_data)
        messages.success(request, 'Раздел обновлён.')
        return redirect('courses:teacher_dashboard')
    return render(request, 'courses/teacher/section_form.html', {
        'form': form, 'title': 'Редактировать раздел', 'object': section,
    })


@teacher_required
def section_delete(request, section_id):
    section = get_object_or_404(Section, pk=section_id)
    if not teacher_service.can_edit_section(request.user, section):
        messages.error(request, 'Вы не прикреплены к этому разделу.')
        return redirect('courses:teacher_dashboard')
    if request.method == 'POST':
        teacher_service.delete_section(section_id)
        messages.success(request, f'Раздел «{section.title}» удалён.')
        return redirect('courses:teacher_dashboard')
    return render(request, 'teacher/confirm_delete.html', {
        'object': section, 'cancel_url': 'courses:teacher_dashboard',
    })


@teacher_required
def lesson_create(request, section_id):
    section = get_object_or_404(Section, pk=section_id)
    if not teacher_service.can_edit_section(request.user, section):
        messages.error(request, 'Вы не прикреплены к этому разделу.')
        return redirect('courses:teacher_dashboard')
    form = LessonForm(request.POST or None)
    if form.is_valid():
        lesson = teacher_service.create_lesson(section, form.cleaned_data)
        messages.success(request, 'Урок создан.')
        return redirect('courses:lesson_manage', lesson_id=lesson.pk)
    return render(request, 'courses/teacher/lesson_form.html', {
        'form': form, 'section': section, 'title': 'Новый урок',
    })


@teacher_required
def lesson_manage(request, lesson_id):
    lesson = get_object_or_404(
        Lesson.objects.select_related('section')
        .prefetch_related('code_examples', 'practical_tasks', 'quizzes'),
        pk=lesson_id,
    )
    return render(request, 'courses/teacher/lesson_manage.html', {'lesson': lesson})


@teacher_required
def lesson_edit(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    if not teacher_service.can_edit_section(request.user, lesson.section):
        messages.error(request, 'Вы не прикреплены к этому разделу.')
        return redirect('courses:teacher_dashboard')
    form = LessonForm(request.POST or None, instance=lesson)
    if form.is_valid():
        teacher_service.update_lesson(lesson, form.cleaned_data)
        messages.success(request, 'Урок обновлён.')
        return redirect('courses:lesson_manage', lesson_id=lesson.pk)
    return render(request, 'courses/teacher/lesson_form.html', {
        'form': form, 'section': lesson.section, 'title': 'Редактировать урок', 'object': lesson,
    })


@teacher_required
def lesson_delete(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    if not teacher_service.can_edit_section(request.user, lesson.section):
        messages.error(request, 'Вы не прикреплены к этому разделу.')
        return redirect('courses:teacher_dashboard')
    section_id = lesson.section_id
    if request.method == 'POST':
        teacher_service.delete_lesson(lesson_id)
        messages.success(request, f'Урок «{lesson.title}» удалён.')
        return redirect('courses:teacher_dashboard')
    return render(request, 'teacher/confirm_delete.html', {
        'object': lesson, 'cancel_url': None, 'cancel_lesson_id': section_id,
    })


@teacher_required
def example_create(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    form = CodeExampleForm(request.POST or None)
    if form.is_valid():
        teacher_service.create_code_example(lesson, form.cleaned_data)
        messages.success(request, 'Пример кода добавлен.')
        return redirect('courses:lesson_manage', lesson_id=lesson.pk)
    return render(request, 'courses/teacher/example_form.html', {
        'form': form, 'lesson': lesson, 'title': 'Новый пример кода',
    })


@teacher_required
def example_edit(request, example_id):
    example = get_object_or_404(CodeExample, pk=example_id)
    form = CodeExampleForm(request.POST or None, instance=example)
    if form.is_valid():
        teacher_service.update_code_example(example, form.cleaned_data)
        messages.success(request, 'Пример кода обновлён.')
        return redirect('courses:lesson_manage', lesson_id=example.lesson_id)
    return render(request, 'courses/teacher/example_form.html', {
        'form': form, 'lesson': example.lesson, 'title': 'Редактировать пример', 'object': example,
    })


@teacher_required
def example_delete(request, example_id):
    example = get_object_or_404(CodeExample, pk=example_id)
    lesson_id = example.lesson_id
    if request.method == 'POST':
        teacher_service.delete_code_example(example_id)
        messages.success(request, 'Пример кода удалён.')
        return redirect('courses:lesson_manage', lesson_id=lesson_id)
    return render(request, 'teacher/confirm_delete.html', {
        'object': example, 'back_lesson_id': lesson_id,
    })


@teacher_required
def task_create(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    form = PracticalTaskForm(request.POST or None)
    if form.is_valid():
        teacher_service.create_practical_task(lesson, form.cleaned_data)
        messages.success(request, 'Задание добавлено.')
        return redirect('courses:lesson_manage', lesson_id=lesson.pk)
    return render(request, 'courses/teacher/task_form.html', {
        'form': form, 'lesson': lesson, 'title': 'Новое задание',
    })


@teacher_required
def task_edit(request, task_id):
    task = get_object_or_404(PracticalTask, pk=task_id)
    form = PracticalTaskForm(request.POST or None, instance=task)
    if form.is_valid():
        teacher_service.update_practical_task(task, form.cleaned_data)
        messages.success(request, 'Задание обновлено.')
        return redirect('courses:lesson_manage', lesson_id=task.lesson_id)
    return render(request, 'courses/teacher/task_form.html', {
        'form': form, 'lesson': task.lesson, 'title': 'Редактировать задание', 'object': task,
    })


@teacher_required
def task_delete(request, task_id):
    task = get_object_or_404(PracticalTask, pk=task_id)
    lesson_id = task.lesson_id
    if request.method == 'POST':
        teacher_service.delete_practical_task(task_id)
        messages.success(request, 'Задание удалено.')
        return redirect('courses:lesson_manage', lesson_id=lesson_id)
    return render(request, 'teacher/confirm_delete.html', {
        'object': task, 'back_lesson_id': lesson_id,
    })


@manager_required
def section_assignments(request):
    from courses.services import manager_service
    sections = manager_service.get_section_assignments()
    teachers = manager_service.get_teachers()
    if request.method == 'POST':
        section_id = request.POST.get('section_id')
        teacher_ids = request.POST.getlist('teacher_ids')
        section = get_object_or_404(Section, pk=section_id)
        manager_service.set_section_teachers(section, teacher_ids)
        messages.success(request, f'Назначения для «{section.title}» обновлены.')
        return redirect('courses:section_assignments')
    return render(request, 'manager/section_assignments.html', {
        'sections': sections, 'teachers': teachers,
    })


@manager_required
def group_list(request):
    groups = teacher_service.get_all_groups()
    return render(request, 'manager/group_list.html', {'groups': groups})


@manager_required
def group_create(request):
    form = StudentGroupForm(request.POST or None)
    if form.is_valid():
        teacher_service.create_group(request.user, form.cleaned_data.copy())
        messages.success(request, 'Группа создана.')
        return redirect('courses:group_list')
    return render(request, 'manager/group_form.html', {'form': form, 'title': 'Новая группа'})


@manager_required
def group_edit(request, group_id):
    group = get_object_or_404(StudentGroup, pk=group_id)
    form = StudentGroupForm(request.POST or None, instance=group)
    if form.is_valid():
        teacher_service.update_group(group, form.cleaned_data.copy())
        messages.success(request, 'Группа обновлена.')
        return redirect('courses:group_list')
    return render(request, 'manager/group_form.html', {
        'form': form, 'title': 'Редактировать группу', 'object': group,
    })


@manager_required
def group_delete(request, group_id):
    group = get_object_or_404(StudentGroup, pk=group_id)
    if request.method == 'POST':
        teacher_service.delete_group(group_id)
        messages.success(request, f'Группа «{group.name}» удалена.')
        return redirect('courses:group_list')
    return render(request, 'teacher/confirm_delete.html', {
        'object': group, 'cancel_url': 'courses:group_list',
    })


@manager_required
def manager_dashboard(request):
    from courses.services import manager_service
    stats = manager_service.get_manager_stats()
    return render(request, 'manager/dashboard.html', stats)


@manager_required
def manager_student_list(request):
    from courses.services import manager_service
    students = manager_service.get_students()
    return render(request, 'manager/student_list.html', {'students': students})


@manager_required
def manager_student_edit(request, student_id):
    from users.models import User
    student = get_object_or_404(User, pk=student_id, role=User.Role.STUDENT)
    form = StudentEditForm(request.POST or None, instance=student)
    if form.is_valid():
        form.save()
        messages.success(request, f'Данные студента {student.get_full_name()} обновлены.')
        return redirect('courses:manager_student_list')
    return render(request, 'manager/student_edit.html', {'form': form, 'student': student})


@manager_required
def invite_list(request):
    invites = RegistrationToken.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'manager/invite_list.html', {'invites': invites})


@manager_required
def invite_create(request):
    form = CreateInviteForm(request.POST or None)
    if form.is_valid():
        token = invite_service.create_invite(request.user, form.cleaned_data)
        link = request.build_absolute_uri(f'/users/register/{token.token}/')
        messages.success(request, f'Ссылка создана: {link}')
        return redirect('courses:invite_list')
    return render(request, 'manager/invite_form.html', {'form': form})


@manager_required
def invite_delete(request, invite_id):
    invite = get_object_or_404(RegistrationToken, pk=invite_id, created_by=request.user)
    if request.method == 'POST':
        invite.delete()
        messages.success(request, 'Ссылка удалена.')
        return redirect('courses:invite_list')
    return render(request, 'teacher/confirm_delete.html', {'object': invite, 'back_lesson_id': None})
