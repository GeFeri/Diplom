import os

from django import forms

from courses.models import Section, Lesson, CodeExample, PracticalTask, StudentGroup


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ('title', 'description', 'order', 'is_published')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ('title', 'content', 'order', 'is_published')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 12}),
        }


class CodeExampleForm(forms.ModelForm):
    class Meta:
        model = CodeExample
        fields = ('title', 'code', 'explanation', 'order')
        widgets = {
            'code': forms.Textarea(attrs={'rows': 10, 'class': 'code-textarea'}),
            'explanation': forms.Textarea(attrs={'rows': 4}),
        }


class PracticalTaskForm(forms.ModelForm):
    class Meta:
        model = PracticalTask
        fields = ('title', 'description', 'hint', 'solution', 'order')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'hint': forms.Textarea(attrs={'rows': 3}),
            'solution': forms.Textarea(attrs={'rows': 6}),
        }


class TaskSubmissionForm(forms.Form):
    file = forms.FileField(label='Файл с работой')

    def clean_file(self):
        f = self.cleaned_data['file']
        allowed = {'.py', '.txt', '.zip', '.pdf', '.docx', '.doc'}
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in allowed:
            raise forms.ValidationError(
                'Недопустимый формат. Разрешено: .py .txt .zip .pdf .docx .doc'
            )
        return f


class GradeSubmissionForm(forms.Form):
    status = forms.ChoiceField(
        label='Результат',
        choices=[('accepted', 'Зачтено'), ('rejected', 'На доработку')],
    )
    comment = forms.CharField(
        label='Комментарий',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )


class StudentGroupForm(forms.ModelForm):
    class Meta:
        model = StudentGroup
        fields = ('name', 'description', 'required_tariff', 'sections')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'sections': forms.CheckboxSelectMultiple(),
        }
