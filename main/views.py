from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm, ApplicationForm
from .models import Application, Category
from django.contrib.auth.decorators import user_passes_test


def home(request):
    completed_apps = Application.objects.filter(status='completed').order_by('-created_at')[:4]
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
def my_applications(request):
    selected_status = request.GET.get('status')

    print(f"[DEBUG] selected_status = '{selected_status}'")

    apps = Application.objects.filter(user=request.user)

    if selected_status:
        apps = apps.filter(status=selected_status)

    apps = apps.order_by('-created_at')

    is_new_selected = selected_status == 'Новая'
    is_in_progress_selected = selected_status == 'Принято в работе'
    is_completed_selected = selected_status == 'Выполнено'

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
def admin_applications(request):
    apps = Application.objects.all().order_by('-created_at')

    if request.method == 'POST':
        app_id = request.POST.get('application_id')
        new_status = request.POST.get('new_status')

        app = get_object_or_404(Application, pk=app_id)

        if app.status != 'Новая':
            messages.error(request, 'Нельзя изменить статус, если заявка уже не "Новая".')
        elif new_status == 'completed':
            if not request.FILES.get('design_image'):
                messages.error(request, 'Для статуса "Выполнено" обязательно прикрепить изображение дизайна.')
            else:
                app.status = 'Выполнено'
                app.design_image = request.FILES['design_image']
                app.save()
                messages.success(request, 'Статус заявки успешно изменён на "Выполнено".')
        elif new_status == 'in_progress':
            comment = request.POST.get('comment')
            if not comment:
                messages.error(request, 'Для статуса "Принято в работу" обязательно указать комментарий.')
            else:
                app.status = 'Принято в работу'
                app.comment = comment
                app.save()
                messages.success(request, 'Статус заявки успешно изменён на "Принято в работу".')
        else:
            messages.error(request, 'Некорректный статус.')

        apps = Application.objects.all().order_by('-created_at')

    for app in apps:
        app.is_new = app.status == 'Новая'
        app.is_in_progress = app.status == 'Принято в работе'
        app.is_completed = app.status == 'Выполнено'

    return render(request, 'main/admin_applications.html', {'applications': apps})
@user_passes_test(is_superuser)
def admin_categories(request):
    categories = Category.objects.all()
    return render(request, 'main/admin_categories.html', {'categories': categories})

@user_passes_test(is_superuser)
def create_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            messages.success(request, 'Категория успешно создана.')
        else:
            messages.error(request, 'Название категории не может быть пустым.')
    return redirect('admin_categories')

@user_passes_test(is_superuser)
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        Application.objects.filter(category=category).delete()
        category.delete()
        messages.success(request, 'Категория и все её заявки успешно удалены.')
    return redirect('admin_categories')