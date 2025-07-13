from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
from .models import Newsletter

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
                from notifications.models import Notification
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