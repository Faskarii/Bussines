from django.contrib import admin
from .models import Course, Lesson, Category, Teacher


class LessonsInline(admin.TabularInline):
    model = Lesson
    fields = ('title', 'video', 'duration')
    extra = 1


@admin.register(Course)
class CoursesAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'display_teachers', 'display_categories', 'is_published', 'created_at')
    inlines = [LessonsInline]
    # filter_horizontal = ('category', 'teacher')
    search_fields = ('name', 'category__name', 'teacher__name')
    list_filter = ('is_published', 'category', 'teacher')

    def display_teachers(self, obj):
        return ", ".join([teacher.name for teacher in obj.teacher.all()])

    display_teachers.short_description = 'Teachers'

    def display_categories(self, obj):
        return ", ".join([category.name for category in obj.category.all()])

    display_categories.short_description = 'Categories'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('get_course_title', 'title')
    list_filter = ('course',)

    def get_course_title(self, obj):
        return f"{obj.course.name}"
    get_course_title.short_description = 'Course'


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', )
