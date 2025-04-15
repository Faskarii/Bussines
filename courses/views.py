from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import CourseForm, LessonForm, TeacherForm
from .models import Course, Lesson, Teacher, Order
from django.core.paginator import Paginator
from lkncmmnt.forms import CommentForm


def index(request):
    courses = Course.objects.filter(is_published=True).prefetch_related('teacher')

    # search code
    course_name = request.GET.get('name')
    logged_user = request.user
    if course_name != '' and course_name is not None:
        courses = courses.filter(title__icontains=course_name)

    # paginator code
    paginator = Paginator(courses, 1)
    page = request.GET.get('page')
    courses = paginator.get_page(page)
    return render(request, 'index.html', {'courses':courses, 'logged_user':logged_user})


def checkout(request):
    if request.method == "POST":
        items = request.POST.get('items', "")
        name = request.POST.get('name', "")
        email = request.POST.get('email', "")
        total = request.POST.get('total', "")
        order = Order(items=items, name=name, email=email, total=total)
        order.save()
        return JsonResponse({
            'success': True,
            'clear_cart': True  # Signal frontend to clear
        })
        redirect('courses:home')
    return render(request, 'checkout.html')


def courseDetail(request, slug):
    logged_user = request.user
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        new_comment = comment_form.save(commit=False)
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        new_comment.course =course
        new_comment.posted_by = f"{logged_user.username}"
        new_comment.save()
        return redirect('courses:course_detail', slug=slug)
    else:
        comment_form = CommentForm()
    course = get_object_or_404(Course, slug=slug)
    lessons = Lesson.objects.filter(course=course)
    return render(request, 'courses/course_detail.html', {'course':course, 'lessons':lessons, 'comment_form':comment_form, 'logged_user':logged_user})


def createCourse(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        form.save()
        return redirect('courses:home')

    else:
        form = CourseForm()
    return render(request, 'courses/create_course.html', {'form':form})


def updateCourse(request, pk):
    course = Course.objects.get(pk=pk)
    form = CourseForm(request.POST or None, instance=course)

    if form.is_valid():
        form.save()
        return redirect('courses:home')

    return render(request, 'courses/create_course.html', {'form':form})


def deleteCourse(request, pk):
    course = Course.objects.get(pk=pk)
    if request.method == 'POST':
        course.delete()
        return redirect('courses:home')
    #ToDo
    # function for this view


def createLesson(reqeust):

    if reqeust.method == 'POST':
        form = LessonForm(reqeust.POST)
        if form.is_valid():
            form.save()
            return redirect('courses:home')

    else:
        form = LessonForm()
    return render(reqeust, 'courses/create_lesson.html', {'form': form})


def updateLesson(request, pk):
    lesson = Lesson.objects.get(pk=pk)
    form = LessonForm(request.POST or None, instance=lesson)
    if form.is_valid():
        form.save()
        return redirect('courses:home')
    return render(request, 'courses/create_lesson.html', {'form':form})


def deleteLesson(request, pk):
    lesson = Lesson.objects.get(pk=pk)
    if request.method == 'POST':
        lesson.delete()
        return redirect('courses:home')
    #TODO
    # function for this view


def createTeacher(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('courses:home')

    else:
        form = TeacherForm()
    return render(request, 'courses/create_teacher.html', {'form':form})


def updateTeacher(request, pk):
    teacher = Teacher.objects.get(pk=pk)
    form = TeacherForm(request.POST or None, instance=teacher)
    if form.is_valid():
        form.save()
        return redirect('courses:home')
    return render(request, 'courses/create_teacher.html', {'form':form})


def deleteTeacher(request, pk):
    teacher = Teacher.objects.get(pk=pk)
    if request.method == 'POST':
        teacher.delete()
        return redirect('courses:home')

    #TODO
    #function for this view


