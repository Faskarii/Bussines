from django.shortcuts import render, redirect, get_object_or_404
from .forms import CourseForm, LessonForm, TeacherForm
from .models import Course, Lesson, Teacher


def index(request):
    courses = Course.objects.filter(is_published=True).prefetch_related('teacher')

    return render(request, 'index.html', {'courses':courses})


def courseDetail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    lessons = Lesson.objects.filter(course=course)
    return render(request, 'courses/course_detail.html', {'course':course, 'lessons':lessons})


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


