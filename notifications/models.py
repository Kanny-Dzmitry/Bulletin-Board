from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.

class Notification(models.Model):
    """Модель уведомлений"""
    NOTIFICATION_TYPES = [
        ('new_response', 'Новый отклик'),
        ('response_accepted', 'Отклик принят'),
        ('response_rejected', 'Отклик отклонен'),
        ('newsletter', 'Новостная рассылка'),
        ('system', 'Системное уведомление'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='Получатель')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True, verbose_name='Отправитель')
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, verbose_name='Тип уведомления')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    message = models.TextField(verbose_name='Сообщение')
    
    # Связь с любой моделью через Generic Foreign Key
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    is_sent = models.BooleanField(default=False, verbose_name='Отправлено по email')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата прочтения')
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.title} для {self.recipient.username}'
    
    def mark_as_read(self):
        """Пометить как прочитанное"""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
    def send_email(self):
        """Отправить уведомление по email"""
        if not self.is_sent and self.recipient.profile.email_notifications:
            from .tasks import send_notification_email_task
            send_notification_email_task.delay(self.pk)
            self.is_sent = True
            self.save()


class EmailTemplate(models.Model):
    """Модель шаблонов email для уведомлений"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название шаблона')
    subject = models.CharField(max_length=200, verbose_name='Тема письма')
    html_content = models.TextField(verbose_name='HTML содержание')
    text_content = models.TextField(blank=True, verbose_name='Текстовое содержание')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Шаблон email'
        verbose_name_plural = 'Шаблоны email'
    
    def __str__(self):
        return self.name
