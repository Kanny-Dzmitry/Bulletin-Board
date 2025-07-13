#!/bin/bash

# Ждем запуска базы данных
echo "Ожидание запуска базы данных..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "База данных запущена!"

# Выполняем миграции
echo "Выполняем миграции..."
python manage.py migrate

# Создаем суперпользователя, если его нет
echo "Создаем суперпользователя..."
python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Суперпользователь admin создан!')
else:
    print('Суперпользователь admin уже существует!')
EOF

# Создаем категории, если их нет
echo "Создаем категории..."
python manage.py shell << EOF
from bulletin_board.models import Category
categories = [
    ('tanks', 'Танки'),
    ('heals', 'Хилы'),
    ('dd', 'ДД'),
    ('traders', 'Торговцы'),
    ('guildmasters', 'Гилдмастеры'),
    ('questgivers', 'Квестгиверы'),
    ('blacksmiths', 'Кузнецы'),
    ('leatherworkers', 'Кожевники'),
    ('alchemists', 'Зельевары'),
    ('spellcasters', 'Мастера заклинаний'),
]

for name, _ in categories:
    category, created = Category.objects.get_or_create(name=name)
    if created:
        print(f'Категория {category.get_name_display()} создана!')
EOF

# Собираем статические файлы
echo "Собираем статические файлы..."
python manage.py collectstatic --noinput

# Запускаем сервер
echo "Запускаем Django сервер..."
exec python manage.py runserver 0.0.0.0:8000 