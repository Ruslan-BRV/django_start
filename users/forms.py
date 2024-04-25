from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

class CustomAuthenticationForm(AuthenticationForm):
    # Добавляем кастомное поле, если это необходимо
    remember_me = forms.BooleanField(required=False, label='Запомнить меня')

    class Meta:
        model = get_user_model()  # Используем текущую активную модель пользователя
        fields = ('username', 'password', 'remember_me')  # Определяем поля, которые будут использоваться

    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        # Применяем Bootstrap 5 классы к полям формы
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})
        self.fields['remember_me'].widget.attrs.update({'class': 'form-check-input'})

class LoginUserForm(forms.Form):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class RegisterUserForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)
    
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'password', 'password2')
        labels = {
            'email': 'E-Mail',
            'first_name': 'Имя'
        }

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают.')  # Проверка совпадения паролей
        return cd['password']

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('Такой email уже существует.')  # Проверка уникальности email
        return email