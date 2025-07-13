from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, ButtonHolder, Submit, Row, Column
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""
    
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'bio', 'location', 'website',
            'game_character_name', 'game_level', 'game_class', 'guild_name',
            'email_notifications', 'newsletter_subscription'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Расскажите о себе...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваш город'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
            'game_character_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя вашего персонажа'
            }),
            'game_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100
            }),
            'game_class': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Класс персонажа'
            }),
            'guild_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название гильдии'
            }),
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'newsletter_subscription': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'avatar': 'Аватар',
            'bio': 'О себе',
            'location': 'Местоположение',
            'website': 'Веб-сайт',
            'game_character_name': 'Имя персонажа',
            'game_level': 'Уровень персонажа',
            'game_class': 'Класс персонажа',
            'guild_name': 'Гильдия',
            'email_notifications': 'Email уведомления',
            'newsletter_subscription': 'Подписка на новости'
        }
        help_texts = {
            'bio': 'Расскажите о себе и своих интересах в игре',
            'game_level': 'Текущий уровень вашего персонажа',
            'email_notifications': 'Получать уведомления об откликах на email',
            'newsletter_subscription': 'Получать новостные рассылки'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                'Персональная информация',
                Row(
                    Column('avatar', css_class='col-md-12'),
                    css_class='mb-3'
                ),
                Row(
                    Column('bio', css_class='col-md-12'),
                    css_class='mb-3'
                ),
                Row(
                    Column('location', css_class='col-md-6'),
                    Column('website', css_class='col-md-6'),
                    css_class='mb-3'
                ),
            ),
            Fieldset(
                'Игровая информация',
                Row(
                    Column('game_character_name', css_class='col-md-6'),
                    Column('game_level', css_class='col-md-6'),
                    css_class='mb-3'
                ),
                Row(
                    Column('game_class', css_class='col-md-6'),
                    Column('guild_name', css_class='col-md-6'),
                    css_class='mb-3'
                ),
            ),
            Fieldset(
                'Настройки уведомлений',
                Row(
                    Column(
                        Field('email_notifications', css_class='form-check-input'),
                        css_class='col-md-6'
                    ),
                    Column(
                        Field('newsletter_subscription', css_class='form-check-input'),
                        css_class='col-md-6'
                    ),
                    css_class='mb-3'
                ),
            ),
            ButtonHolder(
                Submit('submit', 'Сохранить изменения', css_class='btn btn-primary'),
                css_class='d-flex justify-content-end'
            )
        )


class UserUpdateForm(forms.ModelForm):
    """Форма для обновления основной информации пользователя"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Фамилия'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@email.com'
            })
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
                css_class='mb-3'
            ),
            Row(
                Column('email', css_class='col-md-12'),
                css_class='mb-3'
            ),
        )
        
        # Email должен быть уникальным
        self.fields['email'].required = True
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Проверяем, что email уникален, исключая текущего пользователя
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email


class CustomSignupForm(UserCreationForm):
    """Кастомная форма регистрации"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Фамилия'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Логин'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='col-md-12'),
                css_class='mb-3'
            ),
            Row(
                Column('email', css_class='col-md-12'),
                css_class='mb-3'
            ),
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
                css_class='mb-3'
            ),
            Row(
                Column('password1', css_class='col-md-12'),
                css_class='mb-3'
            ),
            Row(
                Column('password2', css_class='col-md-12'),
                css_class='mb-3'
            ),
            ButtonHolder(
                Submit('submit', 'Зарегистрироваться', css_class='btn btn-primary btn-lg w-100'),
                css_class='d-flex justify-content-center'
            )
        )
        
        # Кастомизируем поля паролей
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтверждение пароля'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user 