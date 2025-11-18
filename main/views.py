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