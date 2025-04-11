from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import CourseForm
from .models import Course


def index(request):
    courses = Course.objects.filter(is_published=True).prefetch_related('teacher')

    return render(request, 'index.html', {'courses':courses})


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