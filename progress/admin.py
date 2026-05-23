from django.contrib import admin

from progress.models import UserLessonProgress, TaskSubmission


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'status', 'score', 'time_spent', 'started_at', 'completed_at')
    list_filter = ('status', 'lesson__section')
    search_fields = ('user__username', 'lesson__title')
    readonly_fields = ('started_at', 'completed_at')


@admin.register(TaskSubmission)
class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'status', 'submitted_at', 'reviewed_by', 'reviewed_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'task__title')
    readonly_fields = ('submitted_at', 'reviewed_at')
