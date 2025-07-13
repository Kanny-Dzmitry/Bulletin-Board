from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Post, Response, Newsletter

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_display_name', 'posts_count', 'created_at']
    list_filter = ['name', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    def get_display_name(self, obj):
        return obj.get_name_display()
    get_display_name.short_description = 'Отображаемое название'
    
    def posts_count(self, obj):
        count = obj.posts.count()
        if count > 0:
            url = reverse('admin:bulletin_board_post_changelist')
            return format_html('<a href="{}?category__id__exact={}">{} объявлений</a>', url, obj.id, count)
        return '0 объявлений'
    posts_count.short_description = 'Количество объявлений'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'responses_count', 'created_at']
    list_filter = ['status', 'category', 'created_at', 'author']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    list_per_page = 20
    
    fieldsets = [
        ('Основная информация', {
            'fields': ['title', 'author', 'category', 'status']
        }),
        ('Содержание', {
            'fields': ['content', 'image']
        }),
        ('Временные метки', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def responses_count(self, obj):
        count = obj.responses.count()
        if count > 0:
            url = reverse('admin:bulletin_board_response_changelist')
            return format_html('<a href="{}?post__id__exact={}">{} откликов</a>', url, obj.id, count)
        return '0 откликов'
    responses_count.short_description = 'Количество откликов'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Если создается новый объект
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ['post_title', 'author', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'post__category']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    list_per_page = 20
    
    fieldsets = [
        ('Основная информация', {
            'fields': ['post', 'author', 'status']
        }),
        ('Содержание', {
            'fields': ['content']
        }),
        ('Временные метки', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = 'Объявление'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Если создается новый объект
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipients_count', 'is_sent', 'created_at', 'sent_at']
    list_filter = ['is_sent', 'created_at', 'sent_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'sent_at', 'is_sent']
    filter_horizontal = ['recipients']
    
    fieldsets = [
        ('Основная информация', {
            'fields': ['title', 'content']
        }),
        ('Получатели', {
            'fields': ['recipients'],
            'description': 'Если не выбрать получателей, рассылка будет отправлена всем пользователям с активной подпиской'
        }),
        ('Статус отправки', {
            'fields': ['is_sent', 'sent_at'],
            'classes': ['collapse']
        }),
        ('Временные метки', {
            'fields': ['created_at'],
            'classes': ['collapse']
        }),
    ]
    
    def recipients_count(self, obj):
        return obj.get_recipients_count()
    recipients_count.short_description = 'Количество получателей'
    
    actions = ['send_newsletter']
    
    def send_newsletter(self, request, queryset):
        sent_count = 0
        for newsletter in queryset:
            if not newsletter.is_sent:
                newsletter.send_newsletter()
                sent_count += 1
        
        self.message_user(request, f'Отправлено {sent_count} рассылок')
    send_newsletter.short_description = 'Отправить выбранные рассылки'
    
    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление отправленных рассылок
        if obj and obj.is_sent:
            return False
        return super().has_delete_permission(request, obj)


# Кастомизация админского интерфейса
admin.site.site_header = 'MMORPG Board - Администрирование'
admin.site.site_title = 'MMORPG Board Admin'
admin.site.index_title = 'Добро пожаловать в панель администрирования MMORPG Board'
