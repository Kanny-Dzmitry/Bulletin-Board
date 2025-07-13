from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class UserProfile(models.Model):
    """Модель профиля пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    bio = models.TextField(max_length=500, blank=True, verbose_name='О себе')
    location = models.CharField(max_length=100, blank=True, verbose_name='Местоположение')
    website = models.URLField(blank=True, verbose_name='Веб-сайт')
    
    # Игровые характеристики
    game_character_name = models.CharField(max_length=100, blank=True, verbose_name='Имя игрового персонажа')
    game_level = models.PositiveIntegerField(default=1, verbose_name='Уровень персонажа')
    game_class = models.CharField(max_length=50, blank=True, verbose_name='Класс персонажа')
    guild_name = models.CharField(max_length=100, blank=True, verbose_name='Название гильдии')
    
    # Настройки уведомлений
    email_notifications = models.BooleanField(default=True, verbose_name='Email уведомления')
    newsletter_subscription = models.BooleanField(default=True, verbose_name='Подписка на новости')
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f'Профиль {self.user.username}'
    
    def get_full_name(self):
        """Получить полное имя пользователя"""
        return self.user.get_full_name() or self.user.username
    
    def get_posts_count(self):
        """Получить количество объявлений пользователя"""
        return self.user.posts.filter(status='active').count()
    
    def get_responses_count(self):
        """Получить количество откликов пользователя"""
        return self.user.responses.count()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создать профиль пользователя при создании нового пользователя"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохранить профиль пользователя при сохранении пользователя"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
