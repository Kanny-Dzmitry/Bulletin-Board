from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, ButtonHolder, Submit
from crispy_forms.bootstrap import PrependedText, AppendedText
from .models import Post, Response, Category

class PostForm(ModelForm):
    """Форма для создания и редактирования объявлений"""
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок объявления'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Опишите подробно ваше объявление'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Описание',
            'category': 'Категория',
            'image': 'Изображение'
        }
        help_texts = {
            'title': 'Краткое и понятное название объявления',
            'content': 'Подробное описание с возможностью форматирования',
            'category': 'Выберите подходящую категорию',
            'image': 'Загрузите изображение для объявления (опционально)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            Fieldset(
                'Создание объявления',
                Field('title', css_class='mb-3'),
                Field('category', css_class='mb-3'),
                Field('content', css_class='mb-3'),
                Field('image', css_class='mb-3'),
            ),
            ButtonHolder(
                Submit('submit', 'Опубликовать', css_class='btn btn-primary me-2'),
                css_class='d-flex justify-content-end'
            )
        )
        
        # Добавляем валидацию
        self.fields['title'].required = True
        self.fields['content'].required = True
        self.fields['category'].required = True
        
        # Кастомизируем queryset для категорий
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "Выберите категорию"


class ResponseForm(ModelForm):
    """Форма для создания отклика на объявление"""
    
    class Meta:
        model = Response
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Напишите ваш отклик...'
            })
        }
        labels = {
            'content': 'Ваш отклик'
        }
        help_texts = {
            'content': 'Опишите, почему вы заинтересованы в этом объявлении'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            Field('content', css_class='mb-3'),
            ButtonHolder(
                Submit('submit', 'Отправить отклик', css_class='btn btn-success'),
                css_class='d-flex justify-content-end'
            )
        )
        
        self.fields['content'].required = True


class SearchForm(forms.Form):
    """Форма для поиска объявлений"""
    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск объявлений...'
        }),
        label='Поиск'
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Все категории",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Категория'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'row g-3'
        self.helper.layout = Layout(
            Field('q', wrapper_class='col-md-8'),
            Field('category', wrapper_class='col-md-4'),
            ButtonHolder(
                Submit('submit', 'Найти', css_class='btn btn-primary'),
                css_class='col-12 d-flex justify-content-end'
            )
        )


class ResponseFilterForm(forms.Form):
    """Форма для фильтрации откликов"""
    post = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Все объявления",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Объявление'
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', 'Все статусы'),
            ('pending', 'Ожидает рассмотрения'),
            ('accepted', 'Принят'),
            ('rejected', 'Отклонен'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Статус'
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['post'].queryset = Post.objects.filter(author=user)
        
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'row g-3'
        self.helper.layout = Layout(
            Field('post', wrapper_class='col-md-6'),
            Field('status', wrapper_class='col-md-6'),
            ButtonHolder(
                Submit('submit', 'Фильтровать', css_class='btn btn-secondary'),
                css_class='col-12 d-flex justify-content-end'
            )
        ) 