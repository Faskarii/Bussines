from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CourseForm, LessonForm, TeacherForm
from .models import Course, Lesson, Teacher, Order, Cart, CartItem, OrderItem, ContactMessage, Category, LessonProgress
from django.core.paginator import Paginator
from lkncmmnt.forms import CommentForm
from django.contrib import messages
from exams.models import ExamResult


def home(request):
    # Get all published courses with valid slugs
    courses = Course.objects.filter(is_published=True, slug__isnull=False).exclude(slug='').prefetch_related('teacher')
    logged_user = request.user

    purchased_course_ids = []
    pending_course_ids = []
    taught_course_ids = []
    
    if logged_user.is_authenticated:
        # Get courses taught by the user
        taught_course_ids = Course.objects.filter(teacher=logged_user).values_list('id', flat=True)
        
        # Get purchased courses
        completed_orders = Order.objects.filter(user=logged_user, status='completed')
        for order in completed_orders:
            purchased_course_ids.extend(order.courses.values_list('id', flat=True))
            
        # Get pending orders
        pending_orders = Order.objects.filter(user=logged_user, status='pending')
        for order in pending_orders:
            pending_course_ids.extend(order.courses.values_list('id', flat=True))

    # search code
    course_name = request.GET.get('name')
    if course_name != '' and course_name is not None:
        courses = courses.filter(name__icontains=course_name)

    # paginator code
    paginator = Paginator(courses, 4)  # Show 8 courses per page
    page = request.GET.get('page', 1)  # Default to page 1
    page_obj = paginator.get_page(page)
    
    # محاسبه درصد پیشرفت برای هر دوره
    courses_with_progress = []
    for course in page_obj:
        progress = 0
        if logged_user.is_authenticated and (course.id in purchased_course_ids or course.teacher == logged_user):
            progress = course.get_progress_for_user(logged_user)
        courses_with_progress.append({
            'course': course,
            'progress': progress
        })
    
    return render(request, 'index.html', {
        'page_obj': page_obj,  # Send the paginated queryset
        'courses_with_progress': courses_with_progress,  # Send the courses with progress
        'logged_user': logged_user,
        'purchased_course_ids': purchased_course_ids,
        'pending_course_ids': pending_course_ids,
        'taught_course_ids': taught_course_ids,
        'search_query': course_name
    })


def checkout(request):
    if request.method == "POST":
        name = request.POST.get('name', "")
        email = request.POST.get('email', "")

        cart = request.session.get('cart', {})
        total = sum(float(item['price']) for item in cart.values())
        
        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            total_amount=total,
            status='pending'
        )
        
        # Create order items
        for course_id, item in cart.items():
            course = Course.objects.get(id=course_id)
            OrderItem.objects.create(
                order=order,
                course=course,
                price=float(item['price'])
            )

        request.session['cart'] = {}
        request.session.modified = True

        return JsonResponse({
            'status': 'success',
            'order_id': order.id,
            'redirect_url': '/accounts/profile/?from_checkout=true'
        })

    cart = request.session.get('cart', {})
    total_price = sum(float(item['price']) for item in cart.values())
    total_items = len(cart)
    
    return render(request, 'checkout.html', {
        'cart_items': cart.items(),
        'total_price': total_price,
        'total_items': total_items
    })


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    lessons = course.lessons.all()
    has_purchased = False
    has_pending_order = False
    is_teacher = False
    course_progress = 0
    exam_results = []
    has_passed_exam = False
    
    if request.user.is_authenticated:
        # Check if user is the teacher of this course
        is_teacher = request.user == course.teacher
        
        # Only check for purchases if user is not the teacher
        if not is_teacher:
            has_purchased = OrderItem.objects.filter(
                order__user=request.user,
                order__status='completed',
                course=course
            ).exists()
            
            has_pending_order = OrderItem.objects.filter(
                order__user=request.user,
                order__status='pending',
                course=course
            ).exists()
        
        # Get course progress
        if has_purchased or is_teacher:
            course_progress = course.get_progress_for_user(request.user)
            
            # Get exam results if course has an exam
            if hasattr(course, 'exam'):
                exam_results = course.exam.results.filter(user=request.user).order_by('-completed_at')
                has_passed_exam = exam_results.filter(passed=True).exists()
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.course = course
            comment.posted_by = request.user
            comment.save()
        return redirect('courses:course_detail', slug=slug)
    else:
        comment_form = CommentForm()
    
    # Get progress for each lesson
    lessons_with_progress = []
    for lesson in lessons:
        progress = None
        if request.user.is_authenticated:
            progress = lesson.progress.filter(user=request.user).first()
        lessons_with_progress.append({
            'lesson': lesson,
            'progress': progress
        })
    
    context = {
        'course': course,
        'lessons': lessons_with_progress,
        'comment_form': comment_form,
        'has_purchased': has_purchased,
        'has_pending_order': has_pending_order,
        'is_teacher': is_teacher,
        'course_progress': course_progress,
        'exam_results': exam_results,
        'has_passed_exam': has_passed_exam,
    }
    return render(request, 'courses/course_detail.html', context)


def createCourse(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        form.save()
        return redirect('courses:home')

    else:
        form = CourseForm()
    return render(request, 'courses/create_course.html', {'form':form})


@login_required
def add_to_cart(request, course_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'لطفا ابتدا وارد شوید'})
    
    course = get_object_or_404(Course, id=course_id)
    cart = request.session.get('cart', {})
    
    if str(course_id) not in cart:
        cart[str(course_id)] = {
            'name': course.name,
            'price': course.price,
            'image': course.image.url if course.image else ''
        }
        request.session['cart'] = cart
        request.session.modified = True
        return JsonResponse({
            'status': 'success',
            'message': 'دوره با موفقیت به سبد خرید اضافه شد',
            'count': len(cart)
        })
    return JsonResponse({
        'status': 'error',
        'message': 'این دوره قبلا به سبد خرید اضافه شده است',
        'count': len(cart)
    })


@login_required
def remove_from_cart(request, course_id):
    cart = request.session.get('cart', {})
    if str(course_id) in cart:
        del cart[str(course_id)]
        request.session['cart'] = cart
        request.session.modified = True
        return JsonResponse({
            'status': 'success',
            'message': 'دوره با موفقیت از سبد خرید حذف شد',
            'count': len(cart)
        })
    return JsonResponse({
        'status': 'error',
        'message': 'این دوره در سبد خرید وجود ندارد',
        'count': len(cart)
    })


@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] for item in cart.values())
    
    return render(request, 'courses/cart.html', {
        'cart': cart,
        'total': total
    })


def get_cart_count(request):
    cart = request.session.get('cart', {})
    return JsonResponse({'count': len(cart)})


def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        contact_message = ContactMessage(name=name, email=email, subject=subject, message=message)
        contact_message.save()
        messages.success(request, 'پیام شما با موفقیت ارسال شد. به زودی با شما تماس خواهیم گرفت.')
        return redirect('courses:contact')
    return render(request, 'contact.html')


def staff_required(user):
    return user.is_staff

@login_required
@user_passes_test(staff_required)
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                course = form.save(commit=False)
                course.teacher = request.user
                course.save()
                messages.success(request, 'دوره با موفقیت ایجاد شد.')
                return redirect('courses:course_detail', slug=course.slug)
            except Exception as e:
                messages.error(request, f'خطا در ایجاد دوره: {str(e)}')
        else:
            # Display specific field errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CourseForm()
    
    return render(request, 'courses/create_course.html', {
        'form': form,
        'title': 'افزودن دوره جدید'
    })

@login_required
@user_passes_test(staff_required)
def create_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Check if the user is the teacher of this course
    if request.user != course.teacher:
        messages.error(request, 'شما مجاز به افزودن درس به این دوره نیستید.')
        return redirect('courses:course_detail', slug=course.slug)
    
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, 'درس با موفقیت ایجاد شد.')
            return redirect('courses:course_detail', slug=course.slug)
        else:
            # Show detailed error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = LessonForm()
    
    return render(request, 'courses/create_lesson.html', {
        'form': form,
        'course': course,
        'title': f'افزودن درس جدید به دوره {course.name}'
    })

@login_required
def edit_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    
    # Check if user is the teacher of this course
    if request.user != course.teacher:
        messages.error(request, 'شما دسترسی به ویرایش این دوره را ندارید.')
        return redirect('courses:course_detail', slug=slug)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'دوره با موفقیت ویرایش شد.')
            return redirect('courses:course_detail', slug=slug)
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'courses/edit_course.html', {
        'form': form,
        'course': course
    })


@login_required
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course
    
    # Check if user is the teacher of this course
    if request.user != course.teacher:
        messages.error(request, 'شما دسترسی به ویرایش این درس را ندارید.')
        return redirect('courses:course_detail', slug=course.slug)
    
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'درس با موفقیت ویرایش شد.')
            return redirect('courses:course_detail', slug=course.slug)
    else:
        form = LessonForm(instance=lesson)
    
    return render(request, 'courses/edit_lesson.html', {
        'form': form,
        'lesson': lesson,
        'course': course
    })


@login_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course
    
    # Check if user is the teacher of this course
    if request.user != course.teacher:
        messages.error(request, 'شما دسترسی به حذف این درس را ندارید.')
        return redirect('courses:course_detail', slug=course.slug)
    
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'درس با موفقیت حذف شد.')
        return redirect('courses:course_detail', slug=course.slug)
    
    return render(request, 'courses/delete_lesson.html', {
        'lesson': lesson,
        'course': course
    })


def category_courses(request, slug):
    category = get_object_or_404(Category, slug=slug)
    courses = Course.objects.filter(is_published=True, category=category, slug__isnull=False).exclude(slug='').prefetch_related('teacher', 'liked_by')
    logged_user = request.user

    purchased_course_ids = []
    pending_course_ids = []
    taught_course_ids = []
    
    if logged_user.is_authenticated:
        taught_course_ids = Course.objects.filter(teacher=logged_user).values_list('id', flat=True)
        completed_orders = Order.objects.filter(user=logged_user, status='completed')
        for order in completed_orders:
            purchased_course_ids.extend(order.courses.values_list('id', flat=True))
        pending_orders = Order.objects.filter(user=logged_user, status='pending')
        for order in pending_orders:
            pending_course_ids.extend(order.courses.values_list('id', flat=True))

    paginator = Paginator(courses, 8)  # Show 8 courses per page
    page = request.GET.get('page', 1)  # Default to page 1
    page_obj = paginator.get_page(page)

    # محاسبه درصد پیشرفت برای هر دوره
    courses_with_progress = []
    for course in page_obj:
        progress = 0
        if logged_user.is_authenticated and (course.id in purchased_course_ids or course.teacher == logged_user):
            progress = course.get_progress_for_user(logged_user)
        courses_with_progress.append({
            'course': course,
            'progress': progress
        })

    return render(request, 'index.html', {
        'page_obj': page_obj,
        'courses_with_progress': courses_with_progress,
        'logged_user': logged_user,
        'purchased_course_ids': purchased_course_ids,
        'pending_course_ids': pending_course_ids,
        'taught_course_ids': taught_course_ids,
        'selected_category': category,
    })


@login_required
def mark_lesson_progress(request, lesson_id, content_type):
    if request.method == 'POST':
        try:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            course = lesson.course
            
            # بررسی دسترسی کاربر
            has_access = (
                request.user == course.teacher or
                OrderItem.objects.filter(
                    order__user=request.user,
                    order__status='completed',
                    course=course
                ).exists()
            )
            
            if not has_access:
                return JsonResponse({
                    'status': 'error',
                    'message': 'شما دسترسی لازم برای این عملیات را ندارید'
                }, status=403)
            
            # بررسی نوع محتوا
            if content_type not in ['video', 'pdf']:
                return JsonResponse({
                    'status': 'error',
                    'message': 'نوع محتوا نامعتبر است'
                }, status=400)
            
            # بررسی وجود فایل مورد نظر
            if content_type == 'video' and not lesson.video:
                return JsonResponse({
                    'status': 'error',
                    'message': 'این درس ویدیو ندارد'
                }, status=400)
            elif content_type == 'pdf' and not lesson.pdf_file:
                return JsonResponse({
                    'status': 'error',
                    'message': 'این درس فایل PDF ندارد'
                }, status=400)
            
            # ثبت پیشرفت
            progress, created = LessonProgress.objects.get_or_create(
                user=request.user,
                lesson=lesson,
                defaults={
                    'video_watched': False,
                    'pdf_read': False
                }
            )
            
            if content_type == 'video':
                progress.video_watched = True
            else:  # pdf
                progress.pdf_read = True
            
            progress.save()
            
            # محاسبه درصد پیشرفت کل دوره
            course_progress = course.get_progress_for_user(request.user)
            
            return JsonResponse({
                'status': 'success',
                'progress': course_progress,
                'message': 'پیشرفت با موفقیت ثبت شد'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'خطا در ثبت پیشرفت: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'درخواست نامعتبر'
    }, status=400)


