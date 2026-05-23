from django import forms
from django.forms import inlineformset_factory

from quizzes.models import Quiz, Question, AnswerOption


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ('title', 'description', 'passing_score', 'time_limit', 'is_active')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text', 'order')
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }


AnswerOptionFormSet = inlineformset_factory(
    Question,
    AnswerOption,
    fields=('text', 'is_correct', 'order'),
    extra=4,
    max_num=4,
    can_delete=False,
    widgets={
        'text': forms.TextInput(attrs={'placeholder': 'Вариант ответа'}),
    },
)
