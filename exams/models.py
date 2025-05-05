from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from courses.models import Course

User = get_user_model()

class Exam(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='exam')
    title = models.CharField(max_length=200)
    description = models.TextField()
    passing_score = models.IntegerField(default=80)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"آزمون {self.course.name}"

    class Meta:
        verbose_name = "آزمون"
        verbose_name_plural = "آزمون‌ها"

class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField("متن سوال")
    order = models.PositiveIntegerField("ترتیب سوال", default=0)

    def __str__(self):
        return f"سوال {self.order} از {self.exam}"

    class Meta:
        verbose_name = "سوال"
        verbose_name_plural = "سوالات"
        ordering = ['order']

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField("متن گزینه", max_length=200)
    is_correct = models.BooleanField("گزینه صحیح", default=False)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "گزینه"
        verbose_name_plural = "گزینه‌ها"

class ExamResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_results')
    score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    passed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True)
    certificate_issued = models.BooleanField(default=False)

    def __str__(self):
        return f"نتیجه آزمون {self.exam} - {self.user.get_full_name()}"

    class Meta:
        verbose_name = "نتیجه آزمون"
        verbose_name_plural = "نتایج آزمون‌ها"
