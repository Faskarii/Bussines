from django import forms
from django.utils import timezone
from .models import Category, Teacher, Course, Lesson, Order, persian_slugify


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'description']


class CourseForm(forms.ModelForm):
    new_category = forms.CharField(max_length=100, required=False, label='دسته‌بندی جدید')
    
    class Meta:
        model = Course
        fields = ['name', 'category', 'new_category', 'description', 'price', 'image', 'is_published']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'new_category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام دسته‌بندی جدید را وارد کنید'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False
        self.fields['category'].label = 'انتخاب دسته‌بندی موجود'
        self.fields['category'].empty_label = 'انتخاب کنید...'

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_category = cleaned_data.get('new_category')

        if not category and not new_category:
            raise forms.ValidationError('لطفا یک دسته‌بندی انتخاب کنید یا دسته‌بندی جدید ایجاد کنید.')
        
        if category and new_category:
            raise forms.ValidationError('لطفا فقط یک گزینه را انتخاب کنید: یا دسته‌بندی موجود یا دسته‌بندی جدید.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        new_category = self.cleaned_data.get('new_category')
        
        if new_category:
            category, created = Category.objects.get_or_create(name=new_category)
            instance.category = category
        
        # Generate unique slug
        base_slug = persian_slugify(instance.name)
        slug = base_slug
        counter = 1
        
        while Course.objects.filter(slug=slug).exclude(pk=instance.pk if instance.pk else None).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        instance.slug = slug
        
        if commit:
            instance.save()
        
        return instance


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'video', 'pdf_file', 'duration', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'video': forms.FileInput(attrs={'class': 'form-control'}),
            'pdf_file': forms.FileInput(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = False
        self.fields['order'].required = False
        self.fields['video'].required = False
        self.fields['pdf_file'].required = False
        self.fields['video'].label = 'فایل ویدیو'
        self.fields['pdf_file'].label = 'فایل PDF'

    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        if duration is not None and duration <= 0:
            raise forms.ValidationError('مدت زمان باید بیشتر از صفر باشد.')
        return duration

    def clean_order(self):
        order = self.cleaned_data.get('order')
        if order is not None and order < 0:
            raise forms.ValidationError('ترتیب درس نمی‌تواند منفی باشد.')
        return order

    def clean(self):
        cleaned_data = super().clean()
        video = cleaned_data.get('video')
        pdf_file = cleaned_data.get('pdf_file')
        content = cleaned_data.get('content')

        if not any([video, pdf_file, content]):
            raise forms.ValidationError('حداقل یکی از فیلدهای ویدیو، PDF یا محتوا باید پر شود.')
