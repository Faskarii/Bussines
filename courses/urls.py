from django.urls import path
from . import views


app_name = 'courses'
urlpatterns = [
    path('', views.index, name='home'),
    path('course/create/', views.createCourse, name='create_course'),
    path('course/<int:pk>/', views.updateCourse, name='update_course'),

    # path('lesson/create/', views.createLesson, name='create_lesson'),

]