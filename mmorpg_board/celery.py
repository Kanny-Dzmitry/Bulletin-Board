import os
from celery import Celery
from django.conf import settings

# Устанавливаем модуль настроек по умолчанию для программы 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mmorpg_board.settings')

# Создаем экземпляр Celery
app = Celery('mmorpg_board')

# Используем настройки Django для конфигурации Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем задачи во всех приложениях Django
app.autodiscover_tasks()

# Настройка очередей
app.conf.task_routes = {
    'notifications.tasks.send_notification_email_task': {'queue': 'notifications'},
    'notifications.tasks.send_newsletter_task': {'queue': 'newsletters'},
    'bulletin_board.tasks.send_newsletter_task': {'queue': 'newsletters'},
}

# Настройка beat scheduler для периодических задач
app.conf.beat_schedule = {
    # Пример: очистка старых уведомлений каждый день
    'cleanup-old-notifications': {
        'task': 'notifications.tasks.cleanup_old_notifications',
        'schedule': 86400.0,  # 24 часа
    },
}

app.conf.timezone = 'Europe/Moscow'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 