from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CourseForm, LessonForm, TeacherForm
from .models import Course, Lesson, Teacher, Order, Cart, CartItem, OrderItem
from django.core.paginator import Paginator
from lkncmmnt.forms import CommentForm


def index(request):
    courses = Course.objects.filter(is_published=True).prefetch_related('teacher')
    logged_user = request.user

    purchased_course_ids = []
    if logged_user.is_authenticated:
        completed_orders = Order.objects.filter(user=logged_user, status='completed')
        for order in completed_orders:
            purchased_course_ids.extend(order.courses.values_list('id', flat=True))

    # search code
    course_name = request.GET.get('name')
    if course_name != '' and course_name is not None:
        courses = courses.filter(name__icontains=course_name)

    # paginator code
    paginator = Paginator(courses, 4)
    page = request.GET.get('page')
    courses = paginator.get_page(page)
    
    return render(request, 'index.html', {
        'courses': courses,
        'logged_user': logged_user,
        'purchased_course_ids': purchased_course_ids
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
    
    if request.user.is_authenticated:
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            course=course
        ).exists()
    
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
    
    context = {
        'course': course,
        'lessons': lessons,
        'comment_form': comment_form,
        'has_purchased': has_purchased,
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
            'price': str(course.price),
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
    total = sum(float(item['price']) for item in cart.values())
    
    return render(request, 'courses/cart.html', {
        'cart': cart,
        'total': total
    })


def get_cart_count(request):
    cart = request.session.get('cart', {})
    return JsonResponse({'count': len(cart)})


