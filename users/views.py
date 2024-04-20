from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from users.forms import LoginUserForm


# Create your views here.
def login_user(request):
# Здесь будет реализация входа
    if request.method == 'POST':
        form = LoginUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('catalog') # Временный ответ
            else:
                   form.add_error(None, 'Неверное имя пользователя или пароль')
    else:
        form = LoginUserForm()
    return render(request, 'users/login.html', {'form': form})

def logout_user(request):
# Здесь будет реализация выхода
    logout(request)
    return redirect(reverse('users:login')) # Временный ответ