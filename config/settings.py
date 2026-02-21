import os
from pathlib import Path ## Для работы с путями файлов в кросс-платформенном виде (win, linux mac)
from dotenv import load_dotenv ## Загрузить переменные из файла .env. 

load_dotenv () ## Прочитать файл .env и установить переменные окружения. 

BASE_DIR = Path(__file__).resolve().parent.parent 
"""Что это:

Получить путь к корневой папке проекта.

Пошаговый разбор:

__file__                               → /home/user/project/config/settings.py
Path(__file__)                         → путь как объект Path
Path(__file__).resolve()               → абсолютный путь
Path(__file__).resolve().parent        → /home/user/project/config
Path(__file__).resolve().parent.parent → /home/user/project  (BASE_DIR)  


project/                    ← BASE_DIR (родитель родителя)
├─ config/                  ← .parent (родитель)
│  └─ settings.py           ← __file__ (этот файл)
├─ bot/
├─ manage.py
└─ requirements.txt""" 






SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')
"""Что это:

Секретный ключ Django для шифрования данных.

Как работает:

os.environ.get('SECRET_KEY', 'default_value')
│
├─ Попробуй получить переменную SECRET_KEY из окружения (.env файл)
├─ Если нет в окружении → используй значение по умолчанию
└─ Вернуть значение
Файл .env:

SECRET_KEY=my-super-secret-key-12345
Зачем нужен:

Шифрование сессий (cookies)
Шифрование паролей
CSRF токены"""





DEBUG = os.environ.get('DEBUG', 'True') == 'True'
"""Что означает DEBUG=True:

if DEBUG:
    # ВКЛ В РЕЖИМЕ РАЗРАБОТКИ:
    ✅ Показываем подробные ошибки в браузере
    ✅ Проверяем SQL запросы
    ✅ Перезагружаем код при изменении файлов
    ✅ Не требуется .env файл"""

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'bot',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'school_schedule_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
