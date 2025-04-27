from django.urls import path
from . import views
from lkncmmnt.views import like_course

app_name = 'courses'
urlpatterns = [
    path('', views.index, name='home'),
    path('course/create/', views.createCourse, name='create_course'),
    path('course/<slug:slug>', views.course_detail, name='course_detail'),

    path('cart/add/<int:course_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:course_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/count/', views.get_cart_count, name='get_cart_count'),

    path('checkout/', views.checkout, name="checkout"),
    path('like', like_course, name="like"),

    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
