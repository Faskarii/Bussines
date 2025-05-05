from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.db.models import Sum
import re

def persian_slugify(text):
    # تبدیل اعداد فارسی به انگلیسی
    persian_numbers = '۰۱۲۳۴۵۶۷۸۹'
    english_numbers = '0123456789'
    translation = str.maketrans(persian_numbers, english_numbers)
    text = text.translate(translation)
    
    # تبدیل کاراکترهای فارسی/عربی به انگلیسی
    persian_chars = {
        'ا': 'a', 'آ': 'a', 'ب': 'b', 'پ': 'p', 'ت': 't', 'ث': 's', 
        'ج': 'j', 'چ': 'ch', 'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'z',
        'ر': 'r', 'ز': 'z', 'ژ': 'zh', 'س': 's', 'ش': 'sh', 'ص': 's',
        'ض': 'z', 'ط': 't', 'ظ': 'z', 'ع': 'a', 'غ': 'gh', 'ف': 'f',
        'ق': 'gh', 'ک': 'k', 'گ': 'g', 'ل': 'l', 'م': 'm', 'ن': 'n',
        'و': 'v', 'ه': 'h', 'ی': 'y', 'ئ': 'y', 'ي': 'y', 'ة': 'h',
        ' ': '-', '_': '-'
    }
    
    # تبدیل به حروف کوچک
    text = text.lower()
    
    # تبدیل کاراکترهای فارسی به انگلیسی
    for persian, english in persian_chars.items():
        text = text.replace(persian, english)
    
    # حذف همه کاراکترها به جز حروف انگلیسی، اعداد و خط تیره
    text = ''.join(c for c in text if c.isalnum() or c == '-')
    
    # حذف خط تیره‌های تکراری
    while '--' in text:
        text = text.replace('--', '-')
    
    # حذف خط تیره از ابتدا و انتها
    text = text.strip('-')
    
    # اگر رشته خالی شد، یک مقدار پیش‌فرض برگردان
    if not text:
        text = 'untitled'
    
    return text

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = persian_slugify(self.name)
        super().save(*args, **kwargs)


class Teacher(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=2000)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.IntegerField()
    image = models.ImageField(upload_to='courses/', null=True, blank=True)
    preview_video = models.FileField(upload_to='previews/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses_taught', null=True)
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_courses', blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name='courses')
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = persian_slugify(self.name)
            slug = base_slug
            counter = 1
            
            while Course.objects.filter(slug=slug).exclude(pk=self.pk if self.pk else None).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def total_duration(self):
        return self.lessons.aggregate(total=Sum('duration'))['total'] or 0

    @property
    def enrolled_students(self):
        return self.orderitem_set.filter(order__status='completed').values_list('order__user', flat=True).distinct().count()

    def get_progress_for_user(self, user):
        if not user.is_authenticated:
            return 0
        
        # بررسی دسترسی کاربر
        has_purchased = OrderItem.objects.filter(
            order__user=user,
            order__status='completed',
            course=self
        ).exists()
        
        # اگر کاربر دوره را نخریده باشد، پیشرفت 0 است
        if not has_purchased:
            return 0
        
        total_lessons = self.lessons.count()
        if total_lessons == 0:
            return 100  # اگر درسی وجود نداشت، پیشرفت 100٪ است
        
        completed_lessons = 0
        for lesson in self.lessons.all():
            progress = lesson.progress.filter(user=user).first()
            if progress and progress.is_completed:
                completed_lessons += 1
        
        return int((completed_lessons / total_lessons) * 100)


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True)
    video = models.FileField(upload_to='lessons/videos/', null=True, blank=True)
    pdf_file = models.FileField(upload_to='lessons/pdfs/', null=True, blank=True)
    order = models.IntegerField(default=0)
    duration = models.IntegerField(help_text='Duration in minutes')
    completed_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='completed_lessons', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.name} - {self.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update course's updated_at timestamp
        self.course.save(update_fields=['updated_at'])


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در انتظار پرداخت'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    courses = models.ManyToManyField(Course, through='OrderItem')
    total_amount = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('order', 'course')

    def __str__(self):
        return f"{self.course.name} in Order #{self.order.id}"


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} x {self.course.name}"

    @property
    def total_price(self):
        return self.course.price * self.quantity


class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام و نام خانوادگی")
    email = models.EmailField(verbose_name="ایمیل")
    subject = models.CharField(max_length=200, verbose_name="موضوع")
    message = models.TextField(verbose_name="پیام")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


class LessonProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, related_name='progress')
    video_watched = models.BooleanField(default=False)
    pdf_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username}'s progress in {self.lesson.title}"

    @property
    def is_completed(self):
        # اگر درس هم ویدیو و هم PDF داشت
        if self.lesson.video and self.lesson.pdf_file:
            return self.video_watched and self.pdf_read
        # اگر فقط ویدیو داشت
        elif self.lesson.video:
            return self.video_watched
        # اگر فقط PDF داشت
        elif self.lesson.pdf_file:
            return self.pdf_read
        # اگر هیچ کدام را نداشت
        return True