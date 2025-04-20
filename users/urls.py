from django.urls import path
from . import views


app_name = 'users'
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    # path('logout/', views.logout_view, name='logout'),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('user_order/', views.user_history_orders, name='order'),
    path('user_courses', views.user_courses, name='user_courses')
]