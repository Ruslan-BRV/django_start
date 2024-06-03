from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import logout
from .forms import CustomAuthenticationForm, RegisterUserForm
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import reverse_lazy
from cards.views import MenuMixin
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth import get_user_model
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ProfileUserForm, UserPasswordChangeForm
from cards.models import Card

class LoginUser(MenuMixin, LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}
    redirect_field_name = 'next'

    def get_success_url(self):
        if self.request.POST.get('next', '').strip():
            return self.request.POST.get('next')
        return reverse_lazy('catalog')

class LogoutUser(MenuMixin, LogoutView):
    next_page = reverse_lazy('users:login')


class RegisterUser(MenuMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация'}
    success_url = reverse_lazy('users:register_done')


class RegisterDoneView(MenuMixin, TemplateView):
    template_name = 'users/register_done.html'
    extra_context = {'title': 'Регистрация завершена'}


class ProfileUser(MenuMixin, LoginRequiredMixin, UpdateView):
    model = get_user_model()  # Используем модель текущего пользователя
    form_class = ProfileUserForm  # Связываем с формой профиля пользователя
    template_name = 'users/profile.html'  # Указываем путь к шаблону
    extra_context = {'title': 'Профиль пользователя','active_tab': 'profile'}  # Дополнительный контекст для передачи в шаблон

    def get_success_url(self):
        # URL, на который переадресуется пользователь после успешного обновления
        return reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        # Возвращает объект модели, который должен быть отредактирован
        return self.request.user


class UserPasswordChange(MenuMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'users/password_change_form.html'
    extra_context = {'title': 'Изменение пароля',
                     'active_tab': 'password_change'}
    success_url = reverse_lazy('users:password_change_done')


class UserPasswordChangeDone(MenuMixin, TemplateView):
    template_name = 'users/password_change_done.html'
    extra_context = {'title': 'Пароль изменен успешно'}


class UserCardsView(MenuMixin, ListView):
    model = Card
    template_name = 'users/profile_cards.html'
    context_object_name = 'cards'
    extra_context = {'title': 'Мои карточки',
                     'active_tab': 'profile_cards'}

    def get_queryset(self):
        return Card.objects.filter(author=self.request.user).order_by('-upload_date')