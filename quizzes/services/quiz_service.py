from django.shortcuts import get_object_or_404
from django.utils import timezone

from quizzes.models import Quiz, QuizAttempt, UserAnswer, AnswerOption
from courses.models import Lesson


def all_quizzes_passed(user, lesson):
    active_quizzes = lesson.quizzes.filter(is_active=True)
    if not active_quizzes.exists():
        return True
    for quiz in active_quizzes:
        has_passed = QuizAttempt.objects.filter(
            user=user,
            quiz=quiz,
            status=QuizAttempt.Status.COMPLETED,
            score__gte=quiz.passing_score,
        ).exists()
        if not has_passed:
            return False
    return True


def get_quiz_statuses(user, lesson):
    active_quizzes = lesson.quizzes.filter(is_active=True)
    statuses = {}
    for quiz in active_quizzes:
        statuses[quiz.pk] = QuizAttempt.objects.filter(
            user=user,
            quiz=quiz,
            status=QuizAttempt.Status.COMPLETED,
            score__gte=quiz.passing_score,
        ).exists()
    return statuses


def start_quiz(user, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
    return QuizAttempt.objects.create(user=user, quiz=quiz)


def calculate_score(attempt):
    total_questions = attempt.quiz.questions.count()
    if total_questions == 0:
        return 0.0
    correct_count = 0
    for answer in attempt.answers.select_related('selected_option'):
        if answer.selected_option.is_correct:
            correct_count += 1
    return round(correct_count / total_questions * 100, 2)


def submit_quiz(attempt_id, answers):
    attempt = get_object_or_404(
        QuizAttempt,
        pk=attempt_id,
        status=QuizAttempt.Status.IN_PROGRESS,
    )

    for key, option_id_str in answers.items():
        try:
            question_id = int(key.removeprefix('question_'))
            option_id = int(option_id_str)
        except (ValueError, AttributeError):
            continue

        option = AnswerOption.objects.filter(pk=option_id, question_id=question_id).first()
        if option:
            UserAnswer.objects.update_or_create(
                attempt=attempt,
                question_id=question_id,
                defaults={'selected_option': option},
            )

    attempt.score = calculate_score(attempt)
    attempt.status = QuizAttempt.Status.COMPLETED
    attempt.completed_at = timezone.now()
    attempt.save(update_fields=['score', 'status', 'completed_at'])
    return attempt
