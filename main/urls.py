
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
    path('manage_categories/', views.manage_categories, name='manage_categories'), # Теперь только для админа
    path('admin/change_app_status/', views.view_all_applications_admin, name='view_all_applications_admin'), # Новый URL для админа
    # path('admin/change_status/', views.admin_change_status, name='admin_change_status'), # Опционально, если отдельный эндпоинт
]

