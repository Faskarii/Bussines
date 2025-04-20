from django.shortcuts import render, get_object_or_404, redirect
from courses.models import Course
from django.http import JsonResponse


def like_course(request):
    course_id = request.POST.get('course_id')
    course = get_object_or_404(Course, id=course_id)
    liked = False

    if course.liked_by.filter(id=request.user.id).exists():
        course.liked_by.remove(request.user)
    else:
        course.liked_by.add(request.user)
        liked = True

    return JsonResponse({'liked': liked, 'count': course.liked_by.count()})
