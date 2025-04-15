from django.db import models
from courses.models import Course
from django.conf import settings


class Comment(models.Model):
    posted_by = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    body = models.CharField(max_length=2000)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created', )

    def __str__(self):
        return self.body