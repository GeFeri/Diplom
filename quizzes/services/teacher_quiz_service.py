from django.shortcuts import get_object_or_404

from courses.models import Lesson
from quizzes.models import Quiz, Question


def create_quiz(lesson: Lesson, data: dict) -> Quiz:
    return Quiz.objects.create(lesson=lesson, **data)


def update_quiz(quiz: Quiz, data: dict) -> Quiz:
    for field, value in data.items():
        setattr(quiz, field, value)
    quiz.save()
    return quiz


def delete_quiz(quiz_id: int) -> None:
    get_object_or_404(Quiz, pk=quiz_id).delete()


def create_question_with_options(quiz: Quiz, question_data: dict, options_formset) -> Question:
    question = Question.objects.create(quiz=quiz, **question_data)
    options_formset.instance = question
    options_formset.save()
    return question


def update_question_with_options(question: Question, question_data: dict, options_formset) -> Question:
    for field, value in question_data.items():
        setattr(question, field, value)
    question.save()
    options_formset.instance = question
    options_formset.save()
    return question


def delete_question(question_id: int) -> None:
    get_object_or_404(Question, pk=question_id).delete()
