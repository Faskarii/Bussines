from django.urls import path
from . import views
from lkncmmnt.views import like_course

app_name = 'courses'
urlpatterns = [
    path('', views.index, name='home'),
    path('course/create/', views.createCourse, name='create_course'),
    path('course/<int:pk>/', views.updateCourse, name='update_course'),
    path('course/<slug:slug>', views.courseDetail, name='course_detail'),

    path('lesson/create/', views.createLesson, name='create_lesson'),
    path('lesson/<int:pk>/', views.updateLesson, name='update_lesson'),

    path('teacher/create/', views.createTeacher, name='create_teacher'),
    path('teacher/<int:pk>', views.updateTeacher, name='update_teacher'),

    path('checkout/', views.checkout, name="checkout"),

    path('like', like_course, name="like"),
]