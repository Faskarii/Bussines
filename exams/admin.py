from django.contrib import admin
from .models import Exam, Question, Choice, ExamResult

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    max_num = 4

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'exam', 'order']
    list_filter = ['exam']
    search_fields = ['text']
    inlines = [ChoiceInline]

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'passing_score', 'created_at']
    list_filter = ['course', 'created_at']
    search_fields = ['title', 'description']
    inlines = [QuestionInline]

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'exam', 'score', 'passed', 'completed_at', 'certificate_issued']
    list_filter = ['passed', 'certificate_issued', 'completed_at']
    search_fields = ['user__username', 'user__email', 'exam__title']
    readonly_fields = ['completed_at']
