from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.db.models import Q
from .models import Notification

# Create your views here.

class NotificationListView(LoginRequiredMixin, ListView):
    """Список уведомлений пользователя"""
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Notification.objects.filter(recipient=self.request.user)
        
        # Фильтрация по типу уведомления
        notification_type = self.request.GET.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Фильтрация по статусу прочтения
        read_status = self.request.GET.get('read')
        if read_status == 'unread':
            queryset = queryset.filter(is_read=False)
        elif read_status == 'read':
            queryset = queryset.filter(is_read=True)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Статистика уведомлений
        all_notifications = Notification.objects.filter(recipient=self.request.user)
        context['total_count'] = all_notifications.count()
        context['unread_count'] = all_notifications.filter(is_read=False).count()
        context['read_count'] = all_notifications.filter(is_read=True).count()
        
        # Типы уведомлений
        context['notification_types'] = Notification.NOTIFICATION_TYPES
        
        # Текущие фильтры
        context['current_type'] = self.request.GET.get('type')
        context['current_read_status'] = self.request.GET.get('read')
        
        return context


class NotificationDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр уведомления"""
    model = Notification
    template_name = 'notifications/notification_detail.html'
    context_object_name = 'notification'
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    def get_object(self):
        obj = super().get_object()
        # Автоматически помечаем как прочитанное при просмотре
        if not obj.is_read:
            obj.mark_as_read()
        return obj


class MarkReadView(LoginRequiredMixin, View):
    """Пометить уведомление как прочитанное"""
    
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.mark_as_read()
        messages.success(request, 'Уведомление помечено как прочитанное')
        return redirect('notifications:notification_list')


class MarkAllReadView(LoginRequiredMixin, View):
    """Пометить все уведомления как прочитанные"""
    
    def post(self, request):
        unread_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        )
        count = unread_notifications.count()
        
        for notification in unread_notifications:
            notification.mark_as_read()
        
        messages.success(request, f'Помечено как прочитанные: {count} уведомлений')
        return redirect('notifications:notification_list')


class NotificationDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление уведомления"""
    model = Notification
    template_name = 'notifications/notification_confirm_delete.html'
    success_url = reverse_lazy('notifications:notification_list')
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Уведомление удалено')
        return super().delete(request, *args, **kwargs)


# API Views для AJAX запросов

@login_required
def unread_count(request):
    """Получить количество непрочитанных уведомлений"""
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({
        'count': count,
        'has_unread': count > 0
    })


@login_required
@require_POST
@csrf_exempt
def mark_read_ajax(request, pk):
    """Пометить уведомление как прочитанное через AJAX"""
    try:
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.mark_as_read()
        
        # Обновленное количество непрочитанных
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        return JsonResponse({
            'success': True,
            'message': 'Уведомление помечено как прочитанное',
            'unread_count': unread_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_POST
@csrf_exempt
def mark_all_read_ajax(request):
    """Пометить все уведомления как прочитанные через AJAX"""
    try:
        unread_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        )
        count = unread_notifications.count()
        
        for notification in unread_notifications:
            notification.mark_as_read()
        
        return JsonResponse({
            'success': True,
            'message': f'Помечено как прочитанные: {count} уведомлений',
            'marked_count': count,
            'unread_count': 0
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def notifications_dropdown(request):
    """Получить последние уведомления для выпадающего меню"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:10]
    
    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message[:100],
            'type': notification.notification_type,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%d.%m.%Y %H:%M'),
            'url': f'/notifications/{notification.id}/'
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count,
        'total_count': notifications.count()
    })


# Вспомогательные функции и классы

class NotificationMixin:
    """Миксин для добавления информации о уведомлениях в контекст"""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['unread_notifications_count'] = Notification.objects.filter(
                recipient=self.request.user,
                is_read=False
            ).count()
        return context


def create_notification(recipient, notification_type, title, message, sender=None, content_object=None):
    """Утилитарная функция для создания уведомления"""
    from django.contrib.contenttypes.models import ContentType
    
    notification_data = {
        'recipient': recipient,
        'notification_type': notification_type,
        'title': title,
        'message': message,
    }
    
    if sender:
        notification_data['sender'] = sender
    
    if content_object:
        notification_data['content_type'] = ContentType.objects.get_for_model(content_object)
        notification_data['object_id'] = content_object.pk
    
    notification = Notification.objects.create(**notification_data)
    
    # Отправляем email уведомление
    notification.send_email()
    
    return notification


def bulk_create_notifications(recipients, notification_type, title, message, sender=None):
    """Массовое создание уведомлений"""
    notifications = []
    
    for recipient in recipients:
        notification = Notification(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message
        )
        notifications.append(notification)
    
    created_notifications = Notification.objects.bulk_create(notifications)
    
    # Отправляем email уведомления
    for notification in created_notifications:
        notification.send_email()
    
    return created_notifications
