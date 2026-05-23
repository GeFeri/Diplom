from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from courses.models import Lesson
from quizzes.forms import QuizForm, QuestionForm, AnswerOptionFormSet
from quizzes.models import Quiz, QuizAttempt, Question
from quizzes.services import quiz_service
from quizzes.services import teacher_quiz_service
from users.decorators import teacher_required


@login_required
def quiz_start(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
    if request.method == 'POST':
        attempt = quiz_service.start_quiz(request.user, quiz_id)
        return redirect('quizzes:quiz_attempt', attempt_id=attempt.pk)
    return render(request, 'quizzes/quiz_start.html', {'quiz': quiz})


@login_required
def quiz_attempt(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id, user=request.user)

    if attempt.status == QuizAttempt.Status.COMPLETED:
        return redirect('quizzes:quiz_result', attempt_id=attempt.pk)

    if request.method == 'POST':
        answers = {k: v for k, v in request.POST.items() if k.startswith('question_')}
        attempt = quiz_service.submit_quiz(attempt.pk, answers)
        return redirect('quizzes:quiz_result', attempt_id=attempt.pk)

    questions = attempt.quiz.questions.prefetch_related('options').all()
    return render(request, 'quizzes/quiz_attempt.html', {
        'attempt': attempt,
        'questions': questions,
    })


@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects
        .select_related('quiz')
        .prefetch_related('answers__question', 'answers__selected_option'),
        pk=attempt_id,
        user=request.user,
    )
    return render(request, 'quizzes/quiz_result.html', {'attempt': attempt})


@teacher_required
def quiz_create(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    form = QuizForm(request.POST or None)
    if form.is_valid():
        quiz = teacher_quiz_service.create_quiz(lesson, form.cleaned_data)
        messages.success(request, 'Тест создан. Добавьте вопросы.')
        return redirect('quizzes:question_create', quiz_id=quiz.pk)
    return render(request, 'quizzes/teacher/quiz_form.html', {'form': form, 'lesson': lesson, 'title': 'Новый тест'})


@teacher_required
def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    form = QuizForm(request.POST or None, instance=quiz)
    if form.is_valid():
        teacher_quiz_service.update_quiz(quiz, form.cleaned_data)
        messages.success(request, 'Тест обновлён.')
        return redirect('courses:lesson_manage', lesson_id=quiz.lesson_id)
    return render(request, 'quizzes/teacher/quiz_form.html', {
        'form': form, 'lesson': quiz.lesson, 'title': 'Редактировать тест', 'object': quiz,
    })


@teacher_required
def quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    lesson_id = quiz.lesson_id
    if request.method == 'POST':
        teacher_quiz_service.delete_quiz(quiz_id)
        messages.success(request, f'Тест «{quiz.title}» удалён.')
        return redirect('courses:lesson_manage', lesson_id=lesson_id)
    return render(request, 'teacher/confirm_delete.html', {'object': quiz, 'back_lesson_id': lesson_id})


@teacher_required
def question_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    form = QuestionForm(request.POST or None)
    formset = AnswerOptionFormSet(request.POST or None)
    if form.is_valid() and formset.is_valid():
        teacher_quiz_service.create_question_with_options(quiz, form.cleaned_data, formset)
        messages.success(request, 'Вопрос добавлен.')
        return redirect('courses:lesson_manage', lesson_id=quiz.lesson_id)
    return render(request, 'quizzes/teacher/question_form.html', {
        'form': form, 'formset': formset, 'quiz': quiz, 'title': 'Новый вопрос',
    })


@teacher_required
def question_edit(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    form = QuestionForm(request.POST or None, instance=question)
    formset = AnswerOptionFormSet(request.POST or None, instance=question)
    if form.is_valid() and formset.is_valid():
        teacher_quiz_service.update_question_with_options(question, form.cleaned_data, formset)
        messages.success(request, 'Вопрос обновлён.')
        return redirect('courses:lesson_manage', lesson_id=question.quiz.lesson_id)
    return render(request, 'quizzes/teacher/question_form.html', {
        'form': form, 'formset': formset, 'quiz': question.quiz,
        'title': 'Редактировать вопрос', 'object': question,
    })


@teacher_required
def question_delete(request, question_id):
    question = get_object_or_404(Question.objects.select_related('quiz__lesson'), pk=question_id)
    lesson_id = question.quiz.lesson_id
    if request.method == 'POST':
        teacher_quiz_service.delete_question(question_id)
        messages.success(request, 'Вопрос удалён.')
        return redirect('courses:lesson_manage', lesson_id=lesson_id)
    return render(request, 'teacher/confirm_delete.html', {'object': question, 'back_lesson_id': lesson_id})
