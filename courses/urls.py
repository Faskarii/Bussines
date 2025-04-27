from django.urls import path, re_path
from . import views
from lkncmmnt.views import like_course

app_name = 'courses'
urlpatterns = [
    path('', views.home, name='home'),
    re_path(r'^course/(?P<slug>[\w-]+)/$', views.course_detail, name='course_detail'),
    path('create-course/', views.create_course, name='create_course'),
    path('course/create_lesson/<int:course_id>', views.create_lesson, name='create_lesson'),
    path('course/edit/<slug:slug>/', views.edit_course, name='edit_course'),
    path('lesson/edit/<int:lesson_id>/', views.edit_lesson, name='edit_lesson'),
    path('lesson/delete/<int:lesson_id>/', views.delete_lesson, name='delete_lesson'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:course_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:course_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/count/', views.get_cart_count, name='get_cart_count'),
    path('checkout/', views.checkout, name='checkout'),
    path('like', like_course, name="like"),
]
