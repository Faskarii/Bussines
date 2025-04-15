from decimal import Decimal

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.text import slugify
from django.conf import settings
import json


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Teacher(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=2000)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=50, verbose_name="Course Name")
    slug = models.SlugField(unique=True, blank=True, null=True)
    category = models.ManyToManyField(Category, verbose_name='category')
    teacher = models.ManyToManyField(Teacher, verbose_name='teacher')
    description = models.TextField(max_length=2000, verbose_name="Course Description")
    price = models.IntegerField(verbose_name="Course Price")
    image = models.ImageField(upload_to='course_images/', verbose_name="Course Image", null=True, blank=True)
    preview_video = models.FileField(upload_to='preview_videos/', null=True, blank=True)
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_courses', blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name="Course")
    title = models.CharField(max_length=100, verbose_name="Lesson Title")
    video = models.FileField(upload_to='lesson_videos/', verbose_name="Lesson Video", null=True, blank=True)
    duration = models.IntegerField(verbose_name="Lesson Duration (in minutes)", default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"{self.title} - {self.course.name}"


class Order(models.Model):
    items = models.TextField()
    name = models.CharField(max_length=200)
    email = models.EmailField()
    total = models.CharField(max_length=200)

    def __str__(self):
        return f"Order #{self.id} - {self.name}"


