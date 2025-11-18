from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm, ApplicationForm
from .models import Application, Category
from django.contrib.auth.decorators import user_passes_test


def home(request):
    # Получаем последние 4 заявки со статусом "Выполнено"
    completed_apps = Application.objects.filter(status='Выполнено').order_by('-created_at')[:4]

    # Считаем количество заявок со статусом "Принято в работу"
    in_progress_count = Application.objects.filter(status='Принято в работу').count()

    return render(request, 'main/home.html', {
        'completed_apps': completed_apps,
        'in_progress_count': in_progress_count
    })

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
            messages.success(request, 'Заявка успешно создана!')  # ✅ Исправлено!
            return redirect('my_applications')
    else:
        form = ApplicationForm()
    return render(request, 'main/create_application.html', {'form': form})


@login_required
@login_required
def my_applications(request):
    selected_status = request.GET.get('status')

    # Отладочный вывод
    print(f"[DEBUG] selected_status = '{selected_status}'")

    apps = Application.objects.filter(user=request.user)

    if selected_status:
        apps = apps.filter(status=selected_status)

    apps = apps.order_by('-created_at')

    is_new_selected = selected_status == 'Новая'
    is_in_progress_selected = selected_status == 'Принято в работе'
    is_completed_selected = selected_status == 'Выполнено'

    # Отладочный вывод
    print(f"[DEBUG] is_new_selected = {is_new_selected}")
    print(f"[DEBUG] is_in_progress_selected = {is_in_progress_selected}")
    print(f"[DEBUG] is_completed_selected = {is_completed_selected}")
    print(f"[DEBUG] apps.count() = {apps.count()}")

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

def is_superuser(u):
    return u.is_superuser

@user_passes_test(is_superuser)
@user_passes_test(is_superuser)
def admin_applications(request):
    # Получаем параметры фильтра
    selected_status = request.GET.get('status')
    username_filter = request.GET.get('username')

    # Начинаем с всех заявок
    apps = Application.objects.all()

    # Фильтруем по статусу
    if selected_status:
        apps = apps.filter(status=selected_status)

    # Фильтруем по пользователю
    if username_filter:
        apps = apps.filter(user__username__icontains=username_filter)

    apps = apps.order_by('-created_at')

    return render(request, 'main/admin_applications.html', {
        'applications': apps,
        'selected_status': selected_status,
        'username_filter': username_filter,
    })
@user_passes_test(is_superuser)
def admin_categories(request):
    # Показать все категории
    categories = Category.objects.all()
    return render(request, 'main/admin_categories.html', {'categories': categories})
@user_passes_test(is_superuser)
def update_application_status(request, pk):
    app = get_object_or_404(Application, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        comment = request.POST.get('comment')

        # Убираем проверку на "Новая" — разрешаем менять статус всегда
        # if app.status != 'Новая':
        #     messages.error(request, 'Нельзя изменить статус, если заявка уже не "Новая".')
        #     return redirect('admin_applications')

        # Проверки для новых статусов
        if new_status == 'Выполнено' and not request.FILES.get('design_image'):
            messages.error(request, 'Для статуса "Выполнено" обязательно прикрепить изображение дизайна.')
        elif new_status == 'Принято в работу' and not comment:
            messages.error(request, 'Для статуса "Принято в работу" обязательно указать комментарий.')
        else:
            # Если всё ок — обновляем
            app.status = new_status
            app.comment = comment
            if request.FILES.get('design_image'):
                app.design_image = request.FILES['design_image']
            app.save()
            messages.success(request, 'Статус заявки успешно обновлен.')

    return redirect('admin_applications')
@user_passes_test(is_superuser)
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.get_or_create(name=name.strip())
            messages.success(request, f'Категория "{name}" добавлена.')
        return redirect('admin_categories')
    return redirect('admin_categories')

# Удалить категорию
@user_passes_test(is_superuser)
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()  # Все заявки с этой категорией удалятся автоматически (CASCADE)
    messages.success(request, f'Категория "{category.name}" и связанные заявки удалены.')
    return redirect('admin_categories')