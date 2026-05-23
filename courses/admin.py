from django.contrib import admin

from courses.models import Section, Lesson, CodeExample, PracticalTask, StudentGroup


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'order', 'is_published')
    prepopulated_fields = {'slug': ('title',)} if False else {}


class CodeExampleInline(admin.TabularInline):
    model = CodeExample
    extra = 1
    fields = ('title', 'order', 'code', 'explanation')


class PracticalTaskInline(admin.TabularInline):
    model = PracticalTask
    extra = 1
    fields = ('title', 'order', 'description', 'hint')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_published', 'created_at')
    list_filter = ('is_published',)
    list_editable = ('order', 'is_published')
    search_fields = ('title', 'description')
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'order', 'is_published', 'created_at')
    list_filter = ('is_published', 'section')
    list_editable = ('order', 'is_published')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CodeExampleInline, PracticalTaskInline]


@admin.register(CodeExample)
class CodeExampleAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'order')
    list_filter = ('lesson__section',)
    search_fields = ('title', 'code')


@admin.register(PracticalTask)
class PracticalTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'order')
    list_filter = ('lesson__section',)
    search_fields = ('title', 'description')


@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'required_tariff', 'created_by', 'created_at')
    list_filter = ('required_tariff',)
    search_fields = ('name', 'description')
    filter_horizontal = ('sections',)
