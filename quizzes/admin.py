from django.contrib import admin

from quizzes.models import Quiz, Question, AnswerOption, QuizAttempt, UserAnswer


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 4
    fields = ('text', 'order', 'is_correct')


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('text', 'order')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'passing_score', 'time_limit', 'is_active', 'created_at')
    list_filter = ('is_active', 'lesson__section')
    list_editable = ('is_active',)
    search_fields = ('title', 'description')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'order')
    list_filter = ('quiz',)
    search_fields = ('text',)
    inlines = [AnswerOptionInline]


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct', 'order')
    list_filter = ('is_correct',)
    search_fields = ('text',)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'status', 'score', 'started_at', 'completed_at')
    list_filter = ('status', 'quiz')
    search_fields = ('user__username', 'quiz__title')


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_option')
    list_filter = ('attempt__quiz',)
