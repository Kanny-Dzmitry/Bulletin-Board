from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
from .models import Notification
from bulletin_board.models import Newsletter

@shared_task
def send_notification_email_task(notification_id):
    """Задача для отправки email уведомления"""
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # Проверяем, включены ли email уведомления у пользователя
        if not notification.recipient.profile.email_notifications:
            return f'Email уведомления отключены для пользователя {notification.recipient.username}'
        
        # Подготовка содержимого письма
        subject = f'[MMORPG Board] {notification.title}'
        
        # Базовый контекст для шаблона
        context = {
            'notification': notification,
            'user': notification.recipient,
            'site_name': 'MMORPG Board',
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }
        
        # Выбираем шаблон в зависимости от типа уведомления
        if notification.notification_type == 'new_response':
            template_name = 'notifications/emails/new_response.html'
        elif notification.notification_type == 'response_accepted':
            template_name = 'notifications/emails/response_accepted.html'
        elif notification.notification_type == 'response_rejected':
            template_name = 'notifications/emails/response_rejected.html'
        else:
            template_name = 'notifications/emails/default.html'
        
        # Рендерим HTML и текстовую версию
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        
        # Отправляем email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.recipient.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Помечаем как отправленное
        notification.is_sent = True
        notification.save()
        
        return f'Email уведомление отправлено пользователю {notification.recipient.username}'
        
    except Notification.DoesNotExist:
        return f'Уведомление с ID {notification_id} не найдено'
    except Exception as e:
        return f'Ошибка при отправке email: {str(e)}'


@shared_task
def send_newsletter_task(newsletter_id):
    """Задача для отправки новостной рассылки"""
    try:
        newsletter = Newsletter.objects.get(id=newsletter_id)
        
        # Получаем список получателей
        if newsletter.recipients.exists():
            recipients = newsletter.recipients.all()
        else:
            # Если получатели не указаны, отправляем всем активным пользователям с подпиской
            recipients = User.objects.filter(
                is_active=True,
                profile__newsletter_subscription=True
            )
        
        sent_count = 0
        
        for user in recipients:
            try:
                # Подготовка содержимого письма
                subject = f'[MMORPG Board Newsletter] {newsletter.title}'
                
                context = {
                    'newsletter': newsletter,
                    'user': user,
                    'site_name': 'MMORPG Board',
                    'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
                }
                
                # Рендерим HTML и текстовую версию
                html_message = render_to_string('notifications/emails/newsletter.html', context)
                plain_message = strip_tags(html_message)
                
                # Отправляем email
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                sent_count += 1
                
                # Создаем уведомление в системе
                Notification.objects.create(
                    recipient=user,
                    notification_type='newsletter',
                    title=newsletter.title,
                    message=f'Новая рассылка: {newsletter.title}',
                    is_sent=True
                )
                
            except Exception as e:
                print(f'Ошибка при отправке рассылки пользователю {user.username}: {str(e)}')
        
        return f'Рассылка "{newsletter.title}" отправлена {sent_count} пользователям'
        
    except Newsletter.DoesNotExist:
        return f'Рассылка с ID {newsletter_id} не найдена'
    except Exception as e:
        return f'Ошибка при отправке рассылки: {str(e)}'


@shared_task
def send_bulk_notification_task(user_ids, notification_type, title, message):
    """Задача для массовой отправки уведомлений"""
    try:
        users = User.objects.filter(id__in=user_ids)
        sent_count = 0
        
        for user in users:
            try:
                # Создаем уведомление
                notification = Notification.objects.create(
                    recipient=user,
                    notification_type=notification_type,
                    title=title,
                    message=message
                )
                
                # Отправляем email если включены уведомления
                if user.profile.email_notifications:
                    send_notification_email_task.delay(notification.id)
                
                sent_count += 1
                
            except Exception as e:
                print(f'Ошибка при создании уведомления для пользователя {user.username}: {str(e)}')
        
        return f'Создано {sent_count} уведомлений'
        
    except Exception as e:
        return f'Ошибка при массовой отправке: {str(e)}' 