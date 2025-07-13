from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Notification, EmailTemplate

# Register your models here.

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'sender', 'notification_type', 'is_read', 'is_sent', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_sent', 'created_at']
    search_fields = ['title', 'message', 'recipient__username', 'sender__username']
    readonly_fields = ['created_at', 'read_at', 'content_type', 'object_id']
    list_editable = ['is_read']
    list_per_page = 20
    
    fieldsets = [
        ('Основная информация', {
            'fields': ['recipient', 'sender', 'notification_type', 'title', 'message']
        }),
        ('Связанный объект', {
            'fields': ['content_type', 'object_id'],
            'classes': ['collapse']
        }),
        ('Статус', {
            'fields': ['is_read', 'is_sent', 'read_at']
        }),
        ('Временные метки', {
            'fields': ['created_at'],
            'classes': ['collapse']
        }),
    ]
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Редактирование существующего объекта
            return self.readonly_fields + ['recipient', 'sender', 'notification_type']
        return self.readonly_fields
    
    actions = ['mark_as_read', 'mark_as_unread', 'send_email']
    
    def mark_as_read(self, request, queryset):
        count = 0
        for notification in queryset:
            if not notification.is_read:
                notification.mark_as_read()
                count += 1
        self.message_user(request, f'Помечено как прочитанные: {count} уведомлений')
    mark_as_read.short_description = 'Пометить как прочитанные'
    
    def mark_as_unread(self, request, queryset):
        count = queryset.filter(is_read=True).update(is_read=False, read_at=None)
        self.message_user(request, f'Помечено как непрочитанные: {count} уведомлений')
    mark_as_unread.short_description = 'Пометить как непрочитанные'
    
    def send_email(self, request, queryset):
        count = 0
        for notification in queryset:
            if not notification.is_sent:
                notification.send_email()
                count += 1
        self.message_user(request, f'Отправлено по email: {count} уведомлений')
    send_email.short_description = 'Отправить по email'


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'subject', 'html_content', 'text_content']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Основная информация', {
            'fields': ['name', 'subject']
        }),
        ('Содержание', {
            'fields': ['html_content', 'text_content']
        }),
        ('Временные метки', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Редактирование существующего объекта
            return self.readonly_fields + ['name']
        return self.readonly_fields


# Кастомизация для отображения уведомлений в админке
class NotificationInline(admin.TabularInline):
    model = Notification
    extra = 0
    readonly_fields = ['notification_type', 'title', 'message', 'is_read', 'is_sent', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False
