
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view( next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('create-application/', views.create_application, name='create_application'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('delete-application/<int:pk>/', views.delete_application, name='delete_application'),
    path('filter/', views.filter_applications, name='filter_applications'),
    path('admin-applications/', views.admin_applications, name='admin_applications'),
    path('update-application-status/<int:pk>/', views.update_application_status, name='update_application_status'),
    path('admin-categories/', views.admin_categories, name='admin_categories'),
    path('admin-categories/add/', views.add_category, name='add_category'),
    path('admin-categories/delete/<int:pk>/', views.delete_category, name='delete_category'),
]
