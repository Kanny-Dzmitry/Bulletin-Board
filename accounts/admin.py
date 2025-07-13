from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile

# Register your models here.

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профили пользователей'
    
    fieldsets = [
        ('Персональная информация', {
            'fields': ['avatar', 'bio', 'location', 'website']
        }),
        ('Игровые данные', {
            'fields': ['game_character_name', 'game_level', 'game_class', 'guild_name']
        }),
        ('Настройки уведомлений', {
            'fields': ['email_notifications', 'newsletter_subscription']
        }),
    ]


class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'posts_count', 'responses_count']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'date_joined', 'profile__email_notifications', 'profile__newsletter_subscription']
    
    def posts_count(self, obj):
        count = obj.posts.filter(status='active').count()
        if count > 0:
            return format_html('<span style="color: green;">{}</span>', count)
        return '0'
    posts_count.short_description = 'Объявления'
    
    def responses_count(self, obj):
        count = obj.responses.count()
        if count > 0:
            return format_html('<span style="color: blue;">{}</span>', count)
        return '0'
    responses_count.short_description = 'Отклики'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'game_character_name', 'game_level', 'game_class', 'email_notifications', 'newsletter_subscription', 'created_at']
    list_filter = ['game_class', 'email_notifications', 'newsletter_subscription', 'created_at']
    search_fields = ['user__username', 'user__email', 'game_character_name', 'guild_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Пользователь', {
            'fields': ['user']
        }),
        ('Персональная информация', {
            'fields': ['avatar', 'bio', 'location', 'website']
        }),
        ('Игровые данные', {
            'fields': ['game_character_name', 'game_level', 'game_class', 'guild_name']
        }),
        ('Настройки уведомлений', {
            'fields': ['email_notifications', 'newsletter_subscription']
        }),
        ('Временные метки', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Редактирование существующего объекта
            return self.readonly_fields + ['user']
        return self.readonly_fields


# Перерегистрируем модель User с нашим кастомным админом
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
