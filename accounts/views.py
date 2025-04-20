from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Profile
from courses.models import Course, Order


@login_required
def profile_view(request):
    user = request.user
    completed_orders = Order.objects.filter(user=user, status='completed')
    purchased_course_ids = []
    for order in completed_orders:
        purchased_course_ids.extend(order.courses.values_list('id', flat=True))

    purchased_courses = Course.objects.filter(id__in=purchased_course_ids)
    
    liked_courses = user.liked_courses.all()
    orders = user.orders.all().order_by('-created_at')

    from_checkout = request.GET.get('from_checkout') == 'true'
    
    context = {
        'purchased_courses': purchased_courses,
        'liked_courses': liked_courses,
        'orders': orders,
        'active_tab': 'orders' if from_checkout else 'courses'
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def my_courses_view(request):
    user = request.user
    completed_orders = Order.objects.filter(user=user, status='completed')
    purchased_course_ids = []

    for order in completed_orders:
        purchased_course_ids.extend(order.courses.values_list('id', flat=True))

    courses = Course.objects.filter(id__in=purchased_course_ids)

    for course in courses:
        total_lessons = course.lessons.count()
        if total_lessons > 0:
            completed_lessons = course.lessons.filter(completed_by=user).count()
            course.progress = int((completed_lessons / total_lessons) * 100)
        else:
            course.progress = 0
    
    context = {
        'courses': courses,
    }
    return render(request, 'accounts/my_courses.html', context)


@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        profile = Profile.objects.get_or_create(user=user)[0]

        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()

        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
            profile.save()
        
        messages.success(request, 'پروفایل شما با موفقیت به‌روزرسانی شد.')
        return redirect('accounts:profile')
    
    return redirect('accounts:profile')
