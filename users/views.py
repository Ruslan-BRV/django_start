from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import logout
from .forms import CustomAuthenticationForm, RegisterUserForm
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from cards.views import MenuMixin

class LoginUser(MenuMixin, LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}
    redirect_field_name = 'next'

    def get_success_url(self):
        if self.request.POST.get('next', '').strip():
            return self.request.POST.get('next')
        return reverse_lazy('catalog')

def register(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Устанавливаем пароль
            user.save()
            return redirect('users:register_done')  # Перенаправляем на страницу успешной регистрации
    else:
        form = RegisterUserForm()  # Пустая форма для GET-запроса
    return render(request, 'users/register.html', {'form': form})

# # Create your views here.
# def login_user(request):
# # Здесь будет реализация входа
#     if request.method == 'POST':
#         form = LoginUserForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 next_url = request.POST.get('next', '').strip()  # Получаем next или пустую строку
#                 if next_url:  # Если next_url не пустой
#                     return redirect(next_url)
#                 return redirect('catalog') # Временный ответ
#             else:
#                    form.add_error(None, 'Неверное имя пользователя или пароль')
#     else:
#         form = LoginUserForm()
#     return render(request, 'users/login.html', {'form': form})

def logout_user(request):
# Здесь будет реализация выхода
    logout(request)
    return redirect(reverse('users:login')) # Временный ответ

def signup_user(request):
    return HttpResponse('Регистрация пользователя')