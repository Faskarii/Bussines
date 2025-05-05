from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('exam/<int:course_id>/', views.exam_detail, name='exam_detail'),
    path('exam/<int:course_id>/submit/', views.submit_exam, name='submit_exam'),
    path('result/<int:result_id>/', views.exam_result, name='exam_result'),
    path('course/<int:course_id>/certificate/', views.download_certificate, name='download_certificate'),
] 