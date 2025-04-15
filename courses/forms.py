from django import forms
from django.utils import timezone

from .models import Category, Teacher, Course, Lesson, Order


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'description']


class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = ['name', 'category', 'teacher', 'description', 'price', 'image', 'preview_video', 'is_published']


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['course', 'title', 'video', 'duration']
