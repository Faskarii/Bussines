import json

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings

from courses.models import Order
from .forms import SignUpForm
from .forms import LoginForm
from .models import User, InstructorRequest


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                
                # Handle instructor request
                if form.cleaned_data.get('is_instructor_request'):
                    instructor_request = InstructorRequest.objects.create(user=user)
                    
                    # Send email notification to admin
                    admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@example.com')
                    send_mail(
                        'درخواست جدید مدرس',
                        f'کاربر {user.username} درخواست ثبت نام به عنوان مدرس را دارد.',
                        settings.DEFAULT_FROM_EMAIL,
                        [admin_email],
                        fail_silently=True,
                    )
                    
                    messages.success(request, 'ثبت‌نام شما با موفقیت انجام شد. درخواست مدرس شدن شما برای ادمین ارسال شد.')
                else:
                    messages.success(request, 'ثبت‌نام شما با موفقیت انجام شد. اکنون می‌توانید وارد شوید.')
                
                return redirect('login')
            except Exception as e:
                messages.error(request, 'خطا در ثبت‌نام. لطفاً دوباره تلاش کنید.')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('courses:home')
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


# def logout_view(request):
#     logout(request)
#     return redirect('courses:home')
#     #TODO


def profile(request, pk):
    user = User.objects.get(pk=pk)
    liked_courses = request.user.liked_courses.all()
    return render(request, 'users/profile.html', {'user':user, 'liked_courses':liked_courses})


def user_history_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    user_courses = {}
    for order in orders:
        try:
            items_data = json.loads(order.items) if isinstance(order.items, str) else order.items
            for course_id, details in items_data.items():
                if course_id not in user_courses:
                    user_courses[course_id] = {
                        'name': details[1],
                        'count': details[0],
                        'last_ordered': order.created_at
                    }
        except (TypeError, json.JSONDecodeError):
            continue

    return render(request, 'user_order.html', {
        'orders': orders,
        'user_courses': user_courses
    })


def user_courses(request):
    orders = Order.objects.filter(user=request.user, paid=True).order_by('-created_at')
    user = request.user.username

    user_courses = {}
    for order in orders:
        try:
            items_data = json.loads(order.items) if isinstance(order.items, str) else order.items
            for course_id, details in items_data.items():
                if course_id not in user_courses:
                    user_courses[course_id] = {
                        'name': details[1],
                        'price': details[2],
                        'purchase_date': order.created_at,
                        'order_id': order.id,
                        'quantity': details[0],
                        'last_ordered': order.created_at
                    }
        except (KeyError, json.JSONDecodeError, TypeError) as e:
            continue

    return render(request, 'user_order.html', {
        'orders': orders,
        'user_courses': user_courses,
        'user': user
    })