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
    
    # محاسبه درصد پیشرفت برای دوره‌های خریداری شده
    purchased_courses_with_progress = []
    for course in purchased_courses:
        progress = course.get_progress_for_user(user)
        purchased_courses_with_progress.append({
            'course': course,
            'progress': progress
        })
    
    liked_courses = user.liked_courses.all()
    orders = user.orders.all().order_by('-created_at')

    from_checkout = request.GET.get('from_checkout') == 'true'
    
    context = {
        'purchased_courses': purchased_courses_with_progress,
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

    # محاسبه درصد پیشرفت برای هر دوره
    courses_with_progress = []
    for course in courses:
        progress = course.get_progress_for_user(user)
        courses_with_progress.append({
            'course': course,
            'progress': progress
        })
    
    context = {
        'courses': courses_with_progress,
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
