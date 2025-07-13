# MMORPG Board - Доска объявлений для фанатского сервера

Интернет-ресурс для фанатского сервера MMORPG в виде доски объявлений с системой регистрации, созданием объявлений, откликами и email уведомлениями.

## Функциональность

- ✅ Регистрация пользователей по email с подтверждением
- ✅ Создание и редактирование объявлений с rich text editor
- ✅ 10 категорий объявлений: Танки, Хилы, ДД, Торговцы, Гилдмастеры, Квестгиверы, Кузнецы, Кожевники, Зельевары, Мастера заклинаний
- ✅ Система откликов на объявления
- ✅ Email уведомления при откликах и их принятии/отклонении
- ✅ Приватная страница с откликами на объявления пользователя
- ✅ Фильтрация откликов по объявлениям
- ✅ Новостные рассылки
- ✅ Полноценная админка для управления системой

## Технологии

- **Django 4.2** - основной фреймворк
- **PostgreSQL** - база данных
- **Redis** - кеширование и брокер сообщений
- **Celery** - асинхронная обработка задач
- **Django AllAuth** - аутентификация и регистрация
- **CKEditor** - rich text editor для объявлений
- **Bootstrap 5** - UI фреймворк
- **Docker & Docker Compose** - контейнеризация

## Установка и запуск

### Требования

- Docker
- Docker Compose

### Быстрый старт

1. **Клонируйте репозиторий:**
   ```bash
   git clone <your-repo-url>
   cd mmorpg-board
   ```

2. **Запустите проект:**
   ```bash
   docker-compose up --build
   ```

3. **Дождитесь запуска всех сервисов** (может занять несколько минут при первом запуске)

4. **Откройте в браузере:**
   - Основное приложение: http://localhost:8000
   - Админка: http://localhost:8000/admin/
   - Credentials: `admin` / `admin123`

### Структура проекта

```
mmorpg_board/
├── mmorpg_board/           # Основные настройки проекта
├── accounts/               # Приложение для работы с пользователями
├── bulletin_board/         # Основное приложение с объявлениями
├── notifications/          # Система уведомлений
├── templates/              # HTML шаблоны
├── static/                 # Статические файлы
├── media/                  # Загруженные файлы
├── requirements.txt        # Python зависимости
├── Dockerfile             # Конфигурация Docker
├── docker-compose.yml     # Оркестрация сервисов
└── README.md              # Документация
```

### Сервисы

- **web** - Django приложение (порт 8000)
- **db** - PostgreSQL база данных (порт 5432)
- **redis** - Redis сервер (порт 6379)
- **celery** - Celery worker для обработки задач
- **celery-beat** - Celery beat для периодических задач
- **nginx** - Nginx для раздачи статики (порт 80)

### Основные команды

**Остановка проекта:**
```bash
docker-compose down
```

**Перезапуск проекта:**
```bash
docker-compose restart
```

**Просмотр логов:**
```bash
docker-compose logs -f web
```

**Выполнение команд Django:**
```bash
docker-compose exec web python manage.py <command>
```

**Создание миграций:**
```bash
docker-compose exec web python manage.py makemigrations
```

**Применение миграций:**
```bash
docker-compose exec web python manage.py migrate
```

**Сбор статики:**
```bash
docker-compose exec web python manage.py collectstatic
```

**Создание суперпользователя:**
```bash
docker-compose exec web python manage.py createsuperuser
```

## Использование

### Для пользователей

1. **Регистрация:**
   - Перейдите на `/accounts/signup/`
   - Заполните форму регистрации
   - Подтвердите email (письмо придет в консоль при разработке)

2. **Создание объявления:**
   - Войдите в систему
   - Нажмите "Создать объявление"
   - Выберите категорию
   - Заполните заголовок и описание
   - Опубликуйте объявление

3. **Отклик на объявление:**
   - Найдите интересующее объявление
   - Нажмите "Оставить отклик"
   - Напишите сообщение автору
   - Отправьте отклик

4. **Управление откликами:**
   - Перейдите в "Мои отклики"
   - Просмотрите отклики на ваши объявления
   - Примите или отклоните отклики

### Для администраторов

1. **Админка:** http://localhost:8000/admin/
   - Логин: `admin`, пароль: `admin123`

2. **Управление пользователями:**
   - Просмотр и редактирование профилей
   - Управление разрешениями

3. **Модерация объявлений:**
   - Просмотр всех объявлений
   - Изменение статуса объявлений
   - Удаление неподходящих объявлений

4. **Новостные рассылки:**
   - Создание новых рассылок
   - Выбор получателей
   - Отправка рассылок

## Конфигурация

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DB_NAME=mmorpg_board
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Celery/Redis
CELERY_BROKER_URL=redis://redis:6379
CELERY_RESULT_BACKEND=redis://redis:6379
REDIS_URL=redis://redis:6379/1
```

### Настройка email

Для production окружения настройте реальный SMTP сервер:

1. Измените `EMAIL_BACKEND` на `django.core.mail.backends.smtp.EmailBackend`
2. Укажите правильные настройки SMTP сервера
3. Для Gmail используйте App Passwords

## Мониторинг

### Celery

Для мониторинга задач Celery можно использовать Flower:

```bash
docker-compose exec celery celery -A mmorpg_board flower
```

### Логи

Логи находятся в директории `logs/`:
- `django.log` - логи Django приложения

## Troubleshooting

### Проблемы с базой данных

```bash
# Пересоздание базы данных
docker-compose down -v
docker-compose up --build
```

### Проблемы с статикой

```bash
# Пересбор статики
docker-compose exec web python manage.py collectstatic --clear --noinput
```

### Проблемы с Celery

```bash
# Перезапуск Celery worker
docker-compose restart celery
```

## Разработка

### Локальная разработка

1. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Настройте базу данных:
   ```bash
   python manage.py migrate
   ```

4. Запустите сервер:
   ```bash
   python manage.py runserver
   ```

