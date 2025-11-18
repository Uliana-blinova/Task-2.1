from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm, ApplicationForm
from .models import Application, Category

def home(request):
    completed_applications = Application.objects.filter(
        status='Выполнено'
    ).order_by('-created_at')[:4]


    in_progress_count = Application.objects.filter(
        status='Принято в работу'
    ).count()

    context = {
        'completed_applications': completed_applications,
        'in_progress_count': in_progress_count,
    }
    return render(request, 'main/home.html', context)



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'main/login.html'

class CustomLogoutView(LogoutView):
    next_page = 'home'

@login_required
def profile(request):
    return render(request, 'main/profile.html')

@login_required
def create_application(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.user = request.user
            app.save()
            messages(request, 'Заявка успешно создана!')
            return redirect('my_applications')
    else:
        form = ApplicationForm()
    return render(request, 'main/create_application.html', {'form': form})


@login_required
def my_applications(request):
    selected_status = request.GET.get('status')

    apps = Application.objects.filter(user=request.user)

    if selected_status:
        apps = apps.filter(status=selected_status)

    apps = apps.order_by('-created_at')

    is_new_selected = selected_status == 'Новая'
    is_in_progress_selected = selected_status == 'Принято в работе'
    is_completed_selected = selected_status == 'Выполнено'

    return render(request, 'main/my_applications.html', {
        'applications': apps,
        'selected_status': selected_status,
        'is_new_selected': is_new_selected,
        'is_in_progress_selected': is_in_progress_selected,
        'is_completed_selected': is_completed_selected
    })
@login_required
def delete_application(request, pk):
    app = get_object_or_404(Application, pk=pk, user=request.user)

    if app.status != 'Новая':
        messages(request, 'Нельзя удалить заявку, статус которой не "Новая".')
        return redirect('my_applications')

    if request.method == 'POST':
        app.delete()
        messages(request, 'Заявка успешно удалена.')
        return redirect('my_applications')

    return render(request, 'main/delete_application.html', {'application': app})

def filter_applications(request):
    status = request.GET.get('status')
    applications = Application.objects.all()
    if status:
        applications = applications.filter(status=status)
    return render(request, 'main/applications_list.html', {'applications': applications})
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Application, Category

# Проверка, является ли пользователь суперпользователем
def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser) # Только суперпользователи
def view_all_applications_admin(request):
    """
    Представление для администратора: просмотр и изменение статуса всех заявок.
    """
    applications = Application.objects.select_related('user', 'category').all() # Оптимизация: подгружаем связанные объекты

    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        new_status = request.POST.get('status')

        if new_status in ['Новая', 'Принято в работу', 'Выполнено']:
            app_to_update = get_object_or_404(Application, id=application_id)
            old_status = app_to_update.status
            app_to_update.status = new_status
            app_to_update.save()
            messages.success(request, f'Статус заявки "{app_to_update.title}" изменён с "{old_status}" на "{new_status}".')
        else:
            messages.error(request, 'Недопустимый статус.')

        # После обработки POST возвращаемся к списку
        # (Важно: не используем redirect после POST, чтобы сообщения сохранились)
        # Можно просто перезагрузить страницу с обновленными данными
        # или обновить список в представлении и снова отрендерить шаблон.
        # В простейшем случае - просто отображаем список снова.
        # Django messages автоматически отобразятся при следующем рендере.

    # Фильтрация (опционально)
    status_filter = request.GET.get('status_filter')
    if status_filter:
        applications = applications.filter(status=status_filter)

    categories = Category.objects.all() # Для фильтра по категориям (опционально)
    users = User.objects.all() # Для фильтра по пользователю (опционально)

    context = {
        'applications': applications,
        'categories': categories,
        'users': users,
        'selected_status_filter': status_filter,
    }
    return render(request, 'main/admin_view_applications.html', context)

# Представление для управления категориями (уже есть, но убедимся, что оно защищено)
@login_required
@user_passes_test(is_superuser) # Только суперпользователи
def manage_categories(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            name = request.POST.get('name')
            if name:
                if Category.objects.filter(name=name).exists():
                    messages.error(request, f'Категория "{name}" уже существует.')
                else:
                    Category.objects.create(name=name)
                    messages.success(request, f'Категория "{name}" добавлена.')
            else:
                messages.error(request, 'Название категории не может быть пустым.')

        elif action == 'delete':
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            category.delete() # Учитывайте CASCADE
            messages.success(request, f'Категория "{category.name}" удалена.')

    return render(request, 'main/manage_categories.html', {'categories': categories})

# Не забудьте добавить представление для смены статуса (если хотите отдельный POST-эндпоинт)
# Но в примере ниже статус меняется в том же представлении view_all_applications_admin