from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.utils import timezone

# Create your models here.

class Category(models.Model):
    """Модель для категорий объявлений MMORPG"""
    CATEGORY_CHOICES = [
        ('tanks', 'Танки'),
        ('heals', 'Хилы'),
        ('dd', 'ДД'),
        ('traders', 'Торговцы'),
        ('guildmasters', 'Гилдмастеры'),
        ('questgivers', 'Квестгиверы'),
        ('blacksmiths', 'Кузнецы'),
        ('leatherworkers', 'Кожевники'),
        ('alchemists', 'Зельевары'),
        ('spellcasters', 'Мастера заклинаний'),
    ]
    
    name = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True, verbose_name='Название категории')
    description = models.TextField(blank=True, verbose_name='Описание категории')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()
    
    def get_absolute_url(self):
        return reverse('bulletin_board:category_detail', kwargs={'pk': self.pk})


class Post(models.Model):
    """Модель для объявлений"""
    STATUS_CHOICES = [
        ('active', 'Активно'),
        ('closed', 'Закрыто'),
        ('draft', 'Черновик'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = RichTextField(verbose_name='Содержание')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='Автор')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts', verbose_name='Категория')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    image = models.ImageField(upload_to='post_images/', blank=True, null=True, verbose_name='Изображение')
    
    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.title} - {self.author.username}'
    
    def get_absolute_url(self):
        return reverse('bulletin_board:post_detail', kwargs={'pk': self.pk})
    
    def get_responses_count(self):
        """Получить количество откликов"""
        return self.responses.filter(status='pending').count()
    
    def get_accepted_responses_count(self):
        """Получить количество принятых откликов"""
        return self.responses.filter(status='accepted').count()


class Response(models.Model):
    """Модель для откликов на объявления"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает рассмотрения'),
        ('accepted', 'Принят'),
        ('rejected', 'Отклонен'),
    ]
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='responses', verbose_name='Объявление')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses', verbose_name='Автор отклика')
    content = models.TextField(verbose_name='Содержание отклика')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'
        ordering = ['-created_at']
        unique_together = ['post', 'author']  # Один пользователь может оставить только один отклик на объявление
    
    def __str__(self):
        return f'Отклик от {self.author.username} на "{self.post.title}"'
    
    def get_absolute_url(self):
        return reverse('bulletin_board:response_detail', kwargs={'pk': self.pk})


class Newsletter(models.Model):
    """Модель для новостных рассылок"""
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = RichTextField(verbose_name='Содержание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата отправки')
    is_sent = models.BooleanField(default=False, verbose_name='Отправлено')
    recipients = models.ManyToManyField(User, blank=True, verbose_name='Получатели')
    
    class Meta:
        verbose_name = 'Новостная рассылка'
        verbose_name_plural = 'Новостные рассылки'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def send_newsletter(self):
        """Отправить рассылку"""
        if not self.is_sent:
            from .tasks import send_newsletter_task
            send_newsletter_task.delay(self.pk)
            self.is_sent = True
            self.sent_at = timezone.now()
            self.save()
    
    def get_recipients_count(self):
        """Получить количество получателей"""
        return self.recipients.count() if self.recipients.exists() else User.objects.filter(is_active=True).count()
