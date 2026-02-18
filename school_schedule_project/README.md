# School Schedule Management System

Django-приложение для управления школьным расписанием с PostgreSQL.

---

## Быстрый старт

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Настроить .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Админка: http://localhost:8000/admin/

---

## Структура

```
school_schedule_project/
├── config/              # Настройки Django
│   ├── settings.py     # База данных, приложения, middleware
│   ├── urls.py         # URL routing
│   ├── wsgi.py         # WSGI entry point
│   └── asgi.py         # ASGI entry point
├── bot/                # Главное приложение
│   ├── models.py       # Student, GlobalLesson, PersonalLesson, AdminSettings
│   ├── admin.py        # Кастомная админка с quick-add
│   ├── forms.py        # ScheduleSelectionForm, LessonAddForm
│   └── templates/      # HTML шаблоны
└── manage.py           # Django CLI
```

---

## Модели

### Student
```python
telegram_id (CharField, unique)
name (CharField)
grade (IntegerField, 1-11)
letter (CharField, А-Г)
use_global (BooleanField)
created_at (DateTimeField)
```

### GlobalLesson
```python
grade (IntegerField)
letter (CharField)
day (IntegerField, 1-5)
number (IntegerField)
subject (CharField)

unique_together = ['grade', 'letter', 'day', 'number']
```

### PersonalLesson
```python
student (ForeignKey)
day (IntegerField, 1-5)
number (IntegerField)
subject (CharField)

unique_together = ['student', 'day', 'number']
```

### AdminSettings
```python
contact (CharField)
```

---

## Админка

### Стандартные возможности
- CRUD для всех моделей
- Фильтры, поиск, сортировка

### Кастомная страница "Быстрое добавление"

**URL:** `/admin/bot/globallesson/quick-add/`

**Функционал:**
1. Выбор класса/буквы/дня (сохранение в сессии)
2. Просмотр существующих уроков
3. Быстрое добавление новых
4. Удаление уроков
5. Автоопределение следующего номера

**Реализация:** `GlobalLessonAdmin.quick_add_view()` в `admin.py`

---

## База данных

### PostgreSQL

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}
```

### Создание БД

```sql
CREATE DATABASE school_schedule_db;
CREATE USER django_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE school_schedule_db TO django_user;
```

---

## Переменные окружения (.env)

```env
DB_NAME=school_schedule_db
DB_USER=django_user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=generate-new-key
DEBUG=True
```

---

## Команды

### Миграции
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
```

### Управление
```bash
python manage.py createsuperuser
python manage.py runserver
python manage.py shell
python manage.py collectstatic
```

---

## URL Routing

### config/urls.py
```python
path('admin/', admin.site.urls)
```

### bot/admin.py
```python
path('quick-add/', self.quick_add_view, name='bot_globallesson_quick_add')
```

---

## ORM Examples

```python
# Получить все уроки
lessons = GlobalLesson.objects.filter(grade=9, letter='А', day=1).order_by('number')

# Создать урок
GlobalLesson.objects.create(grade=9, letter='А', day=1, number=1, subject='Математика')

# Обновить
lesson.subject = 'Физика'
lesson.save()

# Удалить
lesson.delete()

# Получить ученика
student = Student.objects.get(telegram_id='123456789')

# Получить расписание ученика
if student.use_global:
    lessons = GlobalLesson.objects.filter(grade=student.grade, letter=student.letter, day=1)
else:
    lessons = student.personal_lessons.filter(day=1)
```

---

## Deployment

### Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Production настройки

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = os.environ.get('SECRET_KEY')
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

```bash
python manage.py collectstatic
```

---

## Зависимости

```
Django==5.0.2
psycopg2-binary==2.9.11
gunicorn==21.2.0
python-dotenv==1.0.0
```

---

## Локализация

```python
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True
```

---

## Лицензия

MIT
