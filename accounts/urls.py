from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views


app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('my-courses/', views.my_courses_view, name='my_courses'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]
