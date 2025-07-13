from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Response, Post
from notifications.models import Notification
from django.contrib.auth.models import User

@receiver(post_save, sender=Response)
def create_response_notification(sender, instance, created, **kwargs):
    """Создать уведомление при создании нового отклика"""
    if created:
        # Уведомление автору объявления о новом отклике
        Notification.objects.create(
            recipient=instance.post.author,
            sender=instance.author,
            notification_type='new_response',
            title='Новый отклик на ваше объявление',
            message=f'Пользователь {instance.author.username} оставил отклик на ваше объявление "{instance.post.title}"',
            content_type=ContentType.objects.get_for_model(Response),
            object_id=instance.pk
        )
        
        # Отправить email уведомление
        notification = Notification.objects.filter(
            recipient=instance.post.author,
            content_type=ContentType.objects.get_for_model(Response),
            object_id=instance.pk
        ).first()
        
        if notification:
            notification.send_email()


@receiver(pre_save, sender=Response)
def response_status_changed(sender, instance, **kwargs):
    """Обработать изменение статуса отклика"""
    if instance.pk:
        try:
            old_instance = Response.objects.get(pk=instance.pk)
            # Если статус изменился с pending на accepted или rejected
            if old_instance.status != instance.status and old_instance.status == 'pending':
                if instance.status == 'accepted':
                    # Уведомление автору отклика о принятии
                    Notification.objects.create(
                        recipient=instance.author,
                        sender=instance.post.author,
                        notification_type='response_accepted',
                        title='Ваш отклик принят!',
                        message=f'Ваш отклик на объявление "{instance.post.title}" был принят пользователем {instance.post.author.username}',
                        content_type=ContentType.objects.get_for_model(Response),
                        object_id=instance.pk
                    )
                elif instance.status == 'rejected':
                    # Уведомление автору отклика об отклонении
                    Notification.objects.create(
                        recipient=instance.author,
                        sender=instance.post.author,
                        notification_type='response_rejected',
                        title='Ваш отклик отклонен',
                        message=f'Ваш отклик на объявление "{instance.post.title}" был отклонен пользователем {instance.post.author.username}',
                        content_type=ContentType.objects.get_for_model(Response),
                        object_id=instance.pk
                    )
                
                # Отправить email уведомление
                notification = Notification.objects.filter(
                    recipient=instance.author,
                    content_type=ContentType.objects.get_for_model(Response),
                    object_id=instance.pk
                ).last()
                
                if notification:
                    notification.send_email()
        except Response.DoesNotExist:
            pass 