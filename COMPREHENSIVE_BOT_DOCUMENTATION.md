# 📚 ИСЧЕРПЫВАЮЩАЯ ДОКУМЕНТАЦИЯ: TELEGRAM БОТ ШКОЛЬНОГО РАСПИСАНИЯ
## Разбор кода "ДО АТОМОВ" для начинающих разработчиков

---

## ОГЛАВЛЕНИЕ
1. [АРХИТЕКТУРА И КОНТЕКСТ](#архитектура-и-контекст)
2. [ИМПОРТЫ И ИНИЦИАЛИЗАЦИЯ](#импорты-и-инициализация)
3. [МОДЕЛИ БАЗЫ ДАННЫХ](#модели-базы-данных)
4. [КОНФИГУРАЦИЯ](#конфигурация)
5. [СЛУЖЕБНЫЕ ФУНКЦИИ](#служебные-функции)
6. [ОБРАБОТЧИКИ КОМАНД](#обработчики-команд)
7. [КЛАВИАТУРЫ](#клавиатуры)
8. [ФОНОВЫЕ ПОТОКИ](#фоновые-потоки)
9. [ГЛАВНЫЙ ЦИКЛ](#главный-цикл)
10. [ПРИМЕРЫ ПОТОКА ДАННЫХ](#примеры-потока-данных)

---

# АРХИТЕКТУРА И КОНТЕКСТ

## 🎯 Что это за проект?

Это **Telegram бот**, который помогает ученикам школы:
- 📅 Просматривать своё расписание уроков (на день, на неделю, завтра)
- ⏰ Получать автоматические напоминания перед уроками
- 📬 Получать утреннюю рассылку с расписанием на день
- ⚙️ Менять свои личные настройки

### Как это работает схематически?

```
┌─────────────────────────────────────────────────────────────┐
│                    TELEGRAM СЕРВЕР                          │
│                  (Облако Telegram)                          │
│                                                             │
│  Пользователь отправляет /start  ──┐                      │
│  Пользователь нажимает кнопку    ──┤                      │
│  Пользователь пишет сообщение    ──┤                      │
│                                   │                        │
└───────────────────────────────────┼────────────────────────┘
                                    │ HTTP запрос
                                    │ (JSON с данными)
                                    ▼
        ┌──────────────────────────────────────────┐
        │       НАШЕ ПРИЛОЖЕНИЕ (Python)           │
        │                                          │
        │  ┌────────────────────────────────────┐ │
        │  │  Обработчик команд (handlers)      │ │
        │  │  - /start                          │ │
        │  │  - Нажатие кнопок                  │ │
        │  │  - Текстовые сообщения             │ │
        │  └────────────────────────────────────┘ │
        │                                          │
        │  ┌────────────────────────────────────┐ │
        │  │  Логика работы                     │ │
        │  │  - Получить расписание             │ │
        │  │  - Найти следующий урок            │ │
        │  │  - Отправить сообщение             │ │
        │  └────────────────────────────────────┘ │
        │                                          │
        │  ┌────────────────────────────────────┐ │
        │  │  Фоновые потоки                    │ │
        │  │  - Рассылка в 6:30                 │ │
        │  │  - Напоминания за 10 минут         │ │
        │  └────────────────────────────────────┘ │
        │                                          │
        │  ┌────────────────────────────────────┐ │
        │  │  Django ORM (взаимодействие с БД)  │ │
        │  │  - Запросы к таблицам              │ │
        │  │  - Сохранение данных               │ │
        │  │  - Фильтрация информации           │ │
        │  └────────────────────────────────────┘ │
        └──────────────────────────────────────────┘
                          │
                          │ SQL запрос
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
        ▼                                   ▼
┌──────────────────┐           ┌─────────────────────┐
│  PostgreSQL БД   │           │ Временные данные    │
│                  │           │ (temp_data dict)    │
│  Таблицы:        │           │                     │
│  - Student       │           │ Используется при:   │
│  - GlobalLesson  │           │ - Выборе класса     │
│  - PersonalLesson│           │ - Создании расписани│
│  - AdminSettings │           │                     │
└──────────────────┘           └─────────────────────┘
```

---

# ИМПОРТЫ И ИНИЦИАЛИЗАЦИЯ

## Строка 1-13: Подключение библиотек и инициализация

```python
import telebot                           # Строка 1
from datetime import datetime, timedelta # Строка 2
import time                              # Строка 3
from threading import Thread             # Строка 4
import pytz                              # Строка 5

from bot.models import Student, GlobalLesson, PersonalLesson, AdminSettings  # Строка 7

TOKEN = '8540461229:AAEY64b5fB0DkOoP96yS6DE9b4MHHmf0JIQ'  # Строка 9
bot = telebot.TeleBot(TOKEN)             # Строка 10

temp_data = {}                           # Строка 12
MSK_TZ = pytz.timezone('Europe/Moscow')  # Строка 13
```

### 📖 Разбор каждого импорта:

#### **Строка 1: `import telebot`**
```python
import telebot
```
- **Что это?** Библиотека для работы с Telegram API
- **Откуда берётся?** Устанавливается через pip (см. requirements.txt: `pyTelegramBotAPI==4.31.0`)
- **Как работает?** 
  - Предоставляет класс `TeleBot`, который подключается к Telegram серверам
  - Позволяет отправлять и получать сообщения
  - Обрабатывает команды, нажатия кнопок, текстовые сообщения
  - Работает по polling механизму (бот постоянно проверяет, есть ли новые сообщения)
- **Пример:** `telebot.types.ReplyKeyboardMarkup()` - создание кнопок в сообщении

#### **Строка 2: `from datetime import datetime, timedelta`**
```python
from datetime import datetime, timedelta
```
- **Что это?** Встроенный модуль Python для работы с датами и временем
- **Два класса:**
  - `datetime` - точная дата и время (год, месяц, день, часы, минуты, секунды)
  - `timedelta` - разница во времени (например, 10 минут)
- **Примеры использования в коде:**
  ```python
  datetime.now(MSK_TZ)  # Текущее время в московском часовом поясе
  timedelta(minutes=10) # Интервал в 10 минут
  ```
- **Логика:** Используется для определения текущего времени и расчёта времени напоминаний

#### **Строка 3: `import time`**
```python
import time
```
- **Что это?** Встроенный модуль для работы со временем
- **Главная функция:** `time.sleep(N)` - "заморозить" выполнение на N секунд
- **Используется в коде:**
  ```python
  time.sleep(30)  # Пауза в 30 секунд в цикле reminder_checker
  time.sleep(60)  # Пауза в 60 секунд в цикле morning_sender
  ```
- **Зачем нужна пауза?** Чтобы не нагружать процессор постоянной работой, делаем перерывы между проверками

#### **Строка 4: `from threading import Thread`**
```python
from threading import Thread
```
- **Что это?** Встроенный модуль для работы с потоками (threading - многопоточность)
- **Что такое поток (thread)?** Это как несколько людей, работающих одновременно:
  - Основной поток: бот обрабатывает команды пользователя
  - Поток 1: отправляет рассылки в 6:30
  - Поток 2: отправляет напоминания за 10 минут
  - Все три работают одновременно!
- **Пример из кода:**
  ```python
  Thread(target=morning_sender, daemon=True).start()
  # Запускает функцию morning_sender в отдельном потоке
  # daemon=True означает, что поток завершится, когда завершится основная программа
  ```

#### **Строка 5: `import pytz`**
```python
import pytz
```
- **Что это?** Библиотека для работы с часовыми поясами
- **Проблема без pytz:**
  ```python
  # БЕЗ pytz: бот будет работать по времени сервера (может быть любой)
  now = datetime.now()  # Может быть UTC, EST, PST и т.д.
  ```
- **С pytz:**
  ```python
  MSK_TZ = pytz.timezone('Europe/Moscow')
  now = datetime.now(MSK_TZ)  # ВСЕГДА московское время
  ```
- **Почему это важно?** В России используется московское время (MSK), а Telegram серверы могут быть где угодно

#### **Строка 7: `from bot.models import ...`**
```python
from bot.models import Student, GlobalLesson, PersonalLesson, AdminSettings
```
- **Что это?** Импорт моделей Django (определены в файле `bot/models.py`)
- **Что такое модели?** Это описание структуры данных в базе данных
  - `Student` - таблица учеников
  - `GlobalLesson` - таблица глобального расписания (для всего класса)
  - `PersonalLesson` - таблица личного расписания (для каждого ученика)
  - `AdminSettings` - таблица с настройками администратора
- **Как использовать в коде:**
  ```python
  student = Student.objects.get(telegram_id=user_id)  # Получить ученика
  lessons = GlobalLesson.objects.filter(grade=10, letter='А')  # Получить уроки класса 10А
  ```

### 🔐 Токен и инициализация бота (Строки 9-10)

```python
TOKEN = '8540461229:AAEY64b5fB0DkOoP96yS6DE9b4MHHmf0JIQ'  # Строка 9
bot = telebot.TeleBot(TOKEN)                              # Строка 10
```

**⚠️ ВАЖНО: БЕЗОПАСНОСТЬ ТОКЕНА**

- **Что такое токен?** Это секретный пароль, который даёт доступ к боту в Telegram
- **Как его получить?** Через BotFather в Telegram
- **Почему это опасно?** Если кто-то узнает токен, он может управлять ботом!
- **ПРОБЛЕМА В КОДЕ:** Токен написан в открытом виде! Это можно исправить:

```python
# НЕПРАВИЛЬНО ❌
TOKEN = '8540461229:AAEY64b5fB0DkOoP96yS6DE9b4MHHmf0JIQ'

# ПРАВИЛЬНО ✅
import os
from dotenv import load_dotenv

load_dotenv()  # Загрузить переменные из .env файла
TOKEN = os.environ.get('BOT_TOKEN')  # Получить из переменной окружения
```

**Строка 10:** `bot = telebot.TeleBot(TOKEN)`
- **Что происходит?** Создаётся объект `bot` класса `TeleBot`
- **Зачем нужен этот объект?** Через него мы отправляем сообщения, обрабатываем команды и т.д.
- **Примеры использования:**
  ```python
  bot.send_message(chat_id, "Привет!")  # Отправить сообщение
  bot.polling()  # Начать слушать Telegram серверы
  ```

### 📦 Временный хранилище (Строка 12)

```python
temp_data = {}  # Строка 12
```

- **Что это?** Словарь (dictionary) на Python, который хранит временные данные
- **Зачем нужен?** При многошаговом взаимодействии с пользователем нужно где-то сохранять промежуточные данные
- **Пример использования:**
  ```python
  # Пользователь нажимает "Сменить класс"
  # Шаг 1: Просим выбрать класс (1-11)
  temp_data[user_id] = {'grade': 10}  # Сохраняем выбор класса
  
  # Шаг 2: Просим выбрать букву (А, Б, В, Г)
  temp_data[user_id]['letter'] = 'А'  # Добавляем букву
  
  # Шаг 3: Сохраняем в БД и удаляем временные данные
  del temp_data[user_id]
  ```

- **Почему не в БД?** БД для постоянных данных, временные данные нужны только во время диалога

### 🕐 Московский часовой пояс (Строка 13)

```python
MSK_TZ = pytz.timezone('Europe/Moscow')  # Строка 13
```

- **Что это?** Объект, представляющий московский часовой пояс
- **Как использовать?**
  ```python
  now = datetime.now(MSK_TZ)  # Текущее время в Москве
  # Результат: 2026-02-18 14:30:45.123456+03:00
  #            │           │                 │
  #            │ дата       │ время           └─ +03:00 (смещение от UTC)
  #            └─────────────────────────────
  ```

- **Почему это критично?** 
  - Без этого напоминания отправлялись бы в неправильное время
  - Рассылка в 6:30 по московскому времени (не по UTC!)

---

## Строки 15-26: Расписание уроков и напоминания

```python
LESSON_TIMES = {
    1: {"start": "08:00", "end": "08:40"},
    2: {"start": "08:50", "end": "09:30"},
    3: {"start": "09:50", "end": "10:30"},
    4: {"start": "10:50", "end": "11:30"},
    5: {"start": "11:40", "end": "12:20"},
    6: {"start": "12:30", "end": "13:10"},
    7: {"start": "13:20", "end": "14:00"},
    8: {"start": "14:10", "end": "14:50"},
}

REMINDER_MINUTES = 10
```

### 📚 Структура `LESSON_TIMES` (Строки 15-24)

```python
LESSON_TIMES = {
    1: {"start": "08:00", "end": "08:40"},  # Урок 1: 08:00-08:40
    # ↑ ключ      ↑ значение (словарь)
}
```

**Что это?** Словарь с номерами уроков как ключи и их временем как значения

**Структура:**
```
LESSON_TIMES = {
    номер_урока: {
        "start": "начало_в_формате_ЧЧ:ММ",
        "end": "конец_в_формате_ЧЧ:ММ"
    }
}
```

**Как использовать?**
```python
# Получить время урока номер 3
time = LESSON_TIMES[3]  # {"start": "09:50", "end": "10:30"}

# Получить время начала урока 3
start_time = LESSON_TIMES[3]["start"]  # "09:50"

# Получить время конца урока 3
end_time = LESSON_TIMES[3]["end"]  # "10:30"
```

**Почему именно такое расписание?**
- 8 уроков в день (это стандарт для большинства школ)
- Между уроками перерывы 10 минут (кроме после 5-го урока - там 20 минут)
- Каждый урок по 40 минут

### ⏰ Напоминания (Строка 26)

```python
REMINDER_MINUTES = 10
```

**Что это?** Количество минут за которое отправляется напоминание до урока

**Логика:**
- Урок начинается в 9:50
- Напоминание отправится в 9:40 (9:50 - 10 минут)
- Это даёт ученику время на подготовку

---

# МОДЕЛИ БАЗЫ ДАННЫХ

## 📊 Что такое модели Django?

Модели - это Python классы, которые описывают структуру таблиц в базе данных.

```
Модель в Python          Таблица в БД          Запись в таблице
┌──────────────────┐    ┌──────────────────┐   ┌─────────────────┐
│ class Student    │    │ Student table    │   │ user_id | name  │
├──────────────────┤    ├──────────────────┤   ├─────────────────┤
│ telegram_id      │───→│ telegram_id      │───│ 12345   | Иван  │
│ name             │───→│ name             │───│ 67890   | Мария │
│ grade            │───→│ grade            │───│         │       │
│ ...              │    │ ...              │   │         │       │
└──────────────────┘    └──────────────────┘   └─────────────────┘
```

## 📝 Разбор модели `Student` (Строки 15-34 в models.py)

```python
class Student(models.Model):
    telegram_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    
    GRADE_CHOICES = [(i, str(i)) for i in range(1, 12)]
    LETTER_CHOICES = [('А', 'А'), ('Б', 'Б'), ('В', 'В'), ('Г', 'Г')]
    
    grade = models.IntegerField(choices=GRADE_CHOICES, null=True, blank=True)
    letter = models.CharField(max_length=1, choices=LETTER_CHOICES, null=True, blank=True)
    use_global = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"
    
    def __str__(self):
        if self.grade and self.letter:
            return f"{self.name} ({self.grade}{self.letter})"
        return self.name
```

### 🔍 Разбор каждого поля:

#### **`telegram_id = models.CharField(max_length=50, unique=True)`**

```
telegram_id (ключевое поле, уникальный идентификатор пользователя)
│
├─ type: CharField  → текстовое поле
├─ max_length: 50   → максимум 50 символов
└─ unique: True     → каждый telegram_id в таблице уникален
                     (не может быть двух одинаковых)

Пример:
┌─────────────────────────────────────────────────────────┐
│ Student таблица                                         │
├───────────────┬──────────┬────────┬──────────┬──────────┤
│ telegram_id   │ name     │ grade  │ letter   │ ...      │
├───────────────┼──────────┼────────┼──────────┼──────────┤
│ 123456789     │ Иван     │ 10     │ А        │          │
│ 987654321     │ Мария    │ 9      │ Б        │          │
│ 555666777     │ Петр     │ 10     │ А        │          │
└───────────────┴──────────┴────────┴──────────┴──────────┘
  ↓
  Все разные!
```

**Как использовать в коде?**
```python
# Когда пользователь отправляет /start
user_id = message.chat.id  # Получаем его telegram_id
student = Student.objects.get(telegram_id=user_id)  # Находим его в БД
```

#### **`name = models.CharField(max_length=100)`**

- **Type:** CharField (текстовое поле)
- **max_length:** 100 символов (достаточно для любого имени)
- **Может быть пусто?** Нет (по умолчанию null=False, blank=False)

**Как заполняется?**
```python
name = message.from_user.first_name or "Ученик"
# Берём первое имя из профиля Telegram
# Если пусто, используем "Ученик"
```

#### **`GRADE_CHOICES` и `LETTER_CHOICES` (Строки 19-20)**

```python
GRADE_CHOICES = [(i, str(i)) for i in range(1, 12)]
# Это список:
# [(1, '1'), (2, '2'), (3, '3'), ..., (11, '11')]
#  ↑ сохраняется   ↑ показывается

LETTER_CHOICES = [('А', 'А'), ('Б', 'Б'), ('В', 'В'), ('Г', 'Г')]
# [('А', 'А'), ('Б', 'Б'), ('В', 'В'), ('Г', 'Г')]
#  ↑ сохраняется   ↑ показывается
```

**Зачем нужны choices?**
- Ограничивают допустимые значения
- Класс может быть только от 1 до 11
- Буква может быть только А, Б, В или Г
- В админке Джанго показывается выпадающий список вместо текстового поля

#### **`grade = models.IntegerField(choices=GRADE_CHOICES, null=True, blank=True)`**

- **type:** IntegerField (целое число)
- **choices:** только значения из GRADE_CHOICES
- **null=True:** может быть пусто в БД (NULL)
- **blank=True:** может быть пусто в форме

**Пример:**
```
Новый ученик регистрируется:
┌─────────────────────────────────────┐
│ telegram_id | name  | grade | letter│
├─────────────────────────────────────┤
│ 123456789   | Иван  | NULL  | NULL  │ ← Пусто, потому что null=True
└─────────────────────────────────────┘

После выбора класса 10А:
┌─────────────────────────────────────┐
│ telegram_id | name  | grade | letter│
├─────────────────────────────────────┤
│ 123456789   | Иван  │ 10    │ А     │ ← Заполнено
└─────────────────────────────────────┘
```

#### **`use_global = models.BooleanField(default=True)`**

```python
use_global = models.BooleanField(default=True)
│           │                      │
│           │                      └─ Новые ученики по умолчанию видят глобальное расписание
│           │
│           └─ BooleanField: только True или False
│
└─ Флаг: смотрит ли ученик глобальное или личное расписание
```

**Как работает логика в коде?**
```python
def get_student_lessons(student, day_num):
    if student.use_global and student.grade and student.letter:
        # Если use_global = True, ищем в глобальном расписании
        lessons = GlobalLesson.objects.filter(
            grade=student.grade,
            letter=student.letter,
            day=day_num
        )
        if lessons.exists():
            return lessons, 'global'
    
    # Если use_global = False или глобального нет, ищем личное
    lessons = PersonalLesson.objects.filter(
        student=student,
        day=day_num
    )
    return lessons, 'personal'
```

#### **`created_at = models.DateTimeField(auto_now_add=True)`**

```python
created_at = models.DateTimeField(auto_now_add=True)
             │                     │
             │                     └─ Автоматически заполняется при создании
             │
             └─ Дата и время в формате: 2026-02-18 14:30:45.123456
```

**Пример:**
```
Когда создаём ученика:
student, created = Student.objects.get_or_create(
    telegram_id=user_id,
    defaults={'name': name}
)

↓

В БД автоматически записывается текущее время:
┌──────────────┬──────────────────────────────┐
│ telegram_id  │ created_at                   │
├──────────────┼──────────────────────────────┤
│ 123456789    │ 2026-02-18 14:30:45.123456  │
└──────────────┴──────────────────────────────┘
```

#### **`class Meta` (Строки 27-29)**

```python
class Meta:
    verbose_name = "Ученик"           # Как называть в админке
    verbose_name_plural = "Ученики"   # Множественное число
```

**Где видно?**
```
Django админка:
┌──────────────────────────────┐
│ ПРИЛОЖЕНИЕ BOT              │
├──────────────────────────────┤
│ Ученики              [+]     │ ← verbose_name_plural
│ ├─ Иван (10А)               │ ← __str__
│ ├─ Мария (9Б)               │
│ └─ Петр (10А)               │
└──────────────────────────────┘
```

#### **`def __str__(self)`**

```python
def __str__(self):
    if self.grade and self.letter:
        return f"{self.name} ({self.grade}{self.letter})"
    return self.name
```

**Что это?** Магический метод Python, который определяет, как выглядит объект при выводе

**Пример:**
```python
student = Student.objects.get(telegram_id=123456789)

print(student)  # Иван (10А)
str(student)    # Иван (10А)
f"{student}"    # Иван (10А)
```

---

## 📖 Модель `GlobalLesson` (Строки 37-53 в models.py)

```python
class GlobalLesson(models.Model):
    DAY_CHOICES = [(1, 'ПН'), (2, 'ВТ'), (3, 'СР'), (4, 'ЧТ'), (5, 'ПТ')]
    
    grade = models.IntegerField(verbose_name='Класс')
    letter = models.CharField(max_length=1, verbose_name='Буква')
    day = models.IntegerField(choices=DAY_CHOICES, verbose_name='День недели')
    number = models.IntegerField(verbose_name='Номер урока')
    subject = models.CharField(max_length=100, verbose_name='Предмет')
    
    class Meta:
        unique_together = ['grade', 'letter', 'day', 'number']
        verbose_name = 'Глобальный урок'
        verbose_name_plural = 'Глобальные уроки'
        ordering = ['grade', 'letter', 'day', 'number']
```

### 🌍 Что такое глобальное расписание?

**Проблема:** Если у класса 10А по 30 учеников, не хотим хранить одно и то же расписание 30 раз

**Решение:** Хранить расписание один раз для всего класса (глобальное), а каждый ученик выбирает, смотреть ли ему глобальное или своё личное

### 📋 Структура таблицы GlobalLesson

```
┌────────┬────────┬──────┬────────┬────────────────┐
│ grade  │ letter │ day  │ number │ subject        │
├────────┼────────┼──────┼────────┼────────────────┤
│ 10     │ А      │ 1    │ 1      │ Математика     │  ← Понедельник, урок 1
│ 10     │ А      │ 1    │ 2      │ Русский язык   │  ← Понедельник, урок 2
│ 10     │ А      │ 1    │ 3      │ История        │  ← Понедельник, урок 3
│ 10     │ А      │ 2    │ 1      │ Физика         │  ← Вторник, урок 1
│ 10     │ А      │ 2    │ 2      │ Математика     │  ← Вторник, урок 2
│ 10     │ Б      │ 1    │ 1      │ Информатика    │  ← Класс 10Б, понедельник, урок 1
└────────┴────────┴──────┴────────┴────────────────┘
```

### 🔐 `unique_together`

```python
unique_together = ['grade', 'letter', 'day', 'number']
```

**Что это?** Гарантирует, что комбинация этих четырёх полей уникальна в таблице

**Пример:**
```
НЕЛЬЗЯ ДОБАВИТЬ ❌
grade=10, letter='А', day=1, number=1, subject='Математика'
grade=10, letter='А', day=1, number=1, subject='Физика'  ← ERROR!
                              ↑
                              Уже есть такая комбинация!

МОЖНО ДОБАВИТЬ ✅
grade=10, letter='А', day=1, number=1, subject='Математика'
grade=10, letter='А', day=1, number=2, subject='Физика'  ← OK!
                              ↑
                              Разный номер урока
```

---

## 📚 Модель `PersonalLesson` (Строки 56-71 в models.py)

```python
class PersonalLesson(models.Model):
    DAY_CHOICES = [(1, 'ПН'), (2, 'ВТ'), (3, 'СР'), (4, 'ЧТ'), (5, 'ПТ')]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='personal_lessons')
    day = models.IntegerField(choices=DAY_CHOICES)
    number = models.IntegerField()
    subject = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ['student', 'day', 'number']
        ordering = ['student', 'day', 'number']
        verbose_name = "Личный урок"
        verbose_name_plural = "Личные уроки"
```

### 👤 Что такое личное расписание?

**Сценарий:** Ученик хочет своё расписание, отличающееся от глобального (например, индивидуальные уроки дополнительные)

**Структура:**
```
┌──────────┬──────┬────────┬────────────────┐
│ student  │ day  │ number │ subject        │
├──────────┼──────┼────────┼────────────────┤
│ Иван     │ 1    │ 1      │ Математика     │  ← Иван, понедельник, урок 1
│ Иван     │ 1    │ 2      │ Русский язык   │  ← Иван, понедельник, урок 2
│ Мария    │ 1    │ 1      │ Физика         │  ← Мария, понедельник, урок 1
│ Мария    │ 1    │ 2      │ Английский     │  ← Мария, понедельник, урок 2
└──────────┴──────┴────────┴────────────────┘
```

### 🔗 `ForeignKey` - связь с таблицей Student

```python
student = models.ForeignKey(
    Student,  # Ссылка на модель Student
    on_delete=models.CASCADE,  # Если удалить ученика, удалить и его уроки
    related_name='personal_lessons'  # Обратная ссылка
)
```

**Визуально:**
```
Student таблица:                PersonalLesson таблица:
┌─────────────────┐            ┌──────────────────────┐
│ id | telegram_id│            │ id | student_id | ... │
├─────────────────┤            ├──────────────────────┤
│ 1  │ 123456789   │ ─────────→ │ 1  │ 1          │ ... │
│ 2  │ 987654321   │ ─────┐    │ 2  │ 1          │ ... │
│    │             │      │    │ 3  │ 2          │ ... │
└─────────────────┘      │    │ 4  │ 2          │ ... │
                         └───→ │ 5  │ 2          │ ... │
                              └──────────────────────┘
```

**Зачем это нужно?**
```python
# Удаляем ученика
student.delete()

# Django автоматически удалит все его PersonalLessons!
# Используется on_delete=models.CASCADE
```

### 🔄 `related_name` - обратная ссылка

```python
related_name='personal_lessons'
```

**Позволяет:**
```python
# Получить ученика
student = Student.objects.get(telegram_id=123456789)

# Получить все его личные уроки
lessons = student.personal_lessons.all()
# Вместо: PersonalLesson.objects.filter(student=student)
```

---

## ⚙️ Модель `AdminSettings` (Строки 4-12 в models.py)

```python
class AdminSettings(models.Model):
    contact = models.CharField(max_length=100, default="@Abumalik08")
    
    class Meta:
        verbose_name = "Настройки"
        verbose_name_plural = "Настройки"
```

**Что это?** Таблица с конфигурацией для администраторов бота

**Пример использования в коде:**
```python
# Когда расписание не найдено, показываем контакт админа
admin_settings = AdminSettings.objects.first()
admin_contact = admin_settings.contact if admin_settings else "@Abumalik08"

bot.send_message(
    message.chat.id,
    f"Напиши господину {admin_contact}"
)
```

---

# КОНФИГУРАЦИЯ

## ⚙️ Django Settings (config/settings.py)

Файл `config/settings.py` содержит конфигурацию всего приложения.

### 🔐 Безопасность

```python
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

**Объяснение:**
- **SECRET_KEY** - секретный ключ для шифрования данных
- **DEBUG** - режим разработки (True) или продакшена (False)
- **ALLOWED_HOSTS** - какие адреса могут обращаться к приложению

### 💾 База данных

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # PostgreSQL
        'NAME': os.environ.get('DB_NAME', 'school_schedule_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

**Как это работает?**

```
Django ORM                    SQL команды            PostgreSQL БД
┌──────────────────┐         ┌──────────────────┐   ┌──────────────┐
│ Student.objects  │         │ SELECT * FROM    │   │ Student table│
│ .get(id=1)       │ ────→   │ student WHERE    │───→│              │
│                  │         │ id=1             │   │              │
└──────────────────┘         └──────────────────┘   └──────────────┘
  (Python)              (автоматически)              (PostgreSQL)
```

### 🌍 Временная зона

```python
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True
```

**Что это?**
- Язык интерфейса - русский
- Часовой пояс - Москва
- Интернационализация включена (поддержка разных языков)

---

# СЛУЖЕБНЫЕ ФУНКЦИИ

## 🔧 Вспомогательные функции для обработки логики

### Функция 1: `get_lesson_time()` (Строки 29-33)

```python
def get_lesson_time(lesson_number):
    lesson = LESSON_TIMES.get(lesson_number)
    if lesson:
        return lesson["start"], lesson["end"]
    return "??:??", "??:??"
```

**Что делает?**
- Получает время начала и конца урока по его номеру
- Если номер неправильный (например, 9 урок), возвращает "??:??"

**Пошаговый разбор:**

```python
# Входные данные:
lesson_number = 3

# Шаг 1:
lesson = LESSON_TIMES.get(3)
# lesson = {"start": "09:50", "end": "10:30"}

# Шаг 2:
if lesson:  # Проверяем, нашли ли урок
    return lesson["start"], lesson["end"]
    # return "09:50", "10:30"
```

**Типы возврата:**
```python
# Правильный номер (1-8)
get_lesson_time(1)  # ("08:00", "08:40")

# Неправильный номер
get_lesson_time(9)  # ("??:??", "??:??")
get_lesson_time(0)  # ("??:??", "??:??")
```

---

### Функция 2: `get_current_lesson_time()` (Строки 36-37)

```python
def get_current_lesson_time():
    return datetime.now(MSK_TZ)
```

**Что делает?** Возвращает текущее время в московском часовом поясе

**Почему нужна отдельная функция?**
- Облегчает замену логики позже
- Можно легко переключиться на другой часовой пояс
- Удобнее для тестирования

**Как использовать:**
```python
now = get_current_lesson_time()
# now = datetime.datetime(2026, 2, 18, 14, 30, 45, 123456, 
#                         tzinfo=<DstTzInfo 'Europe/Moscow' MSK+3:00:00 STD>)

print(now.hour)        # 14
print(now.minute)      # 30
print(now.isoweekday())  # 3 (среда)
```

---

### Функция 3: `normalize_letter()` (Строки 40-44)

```python
def normalize_letter(letter):
    if not letter:
        return None
    letter = letter.upper().strip()
    return letter if letter in ['А', 'Б', 'В', 'Г'] else None
```

**Что делает?** Проверяет и форматирует букву класса

**Пошаговый разбор:**

```python
# Пример 1: Valid буква
input: "а"
├─ Шаг 1: if not letter → False (буква есть)
├─ Шаг 2: letter = letter.upper().strip() → "А"
├─ Шаг 3: "А" in ['А', 'Б', 'В', 'Г'] → True
└─ return: "А"

# Пример 2: Invalid буква
input: "х"
├─ Шаг 1: if not letter → False (буква есть)
├─ Шаг 2: letter = letter.upper().strip() → "Х"
├─ Шаг 3: "Х" in ['А', 'Б', 'В', 'Г'] → False
└─ return: None

# Пример 3: Empty буква
input: None / ""
├─ Шаг 1: if not letter → True
└─ return: None
```

**Как использовать:**
```python
normalize_letter("а")     # "А"
normalize_letter("б")     # "Б"
normalize_letter("х")     # None
normalize_letter(None)    # None
normalize_letter("")      # None
```

---

### Функция 4: `get_student_lessons()` (Строки 47-61)

```python
def get_student_lessons(student, day_num):
    if student.use_global and student.grade and student.letter:
        lessons = GlobalLesson.objects.filter(
            grade=student.grade,
            letter=student.letter,
            day=day_num
        ).order_by('number')
        if lessons.exists():
            return lessons, 'global'
    
    lessons = PersonalLesson.objects.filter(
        student=student,
        day=day_num
    ).order_by('number')
    return lessons, 'personal'
```

**Это КЛЮЧЕВАЯ функция для логики бота!**

**Что делает?**
- Получает расписание для ученика на конкретный день
- Выбирает между глобальным и личным расписанием
- Сортирует уроки по номеру

**Алгоритм (flowchart):**

```
         START
           │
           ▼
    ┌──────────────────┐
    │ Ученик выбрал    │
    │ глобальное AND   │ ← Проверяем use_global
    │ у него есть      │
    │ класс и буква?   │
    └──────┬───────────┘
           │
      ┌────┴────┐
      │          │
   YES│          │NO
      ▼          ▼
  ┌────────┐   ┌────────────────┐
  │ Ищем в │   │ Ищем в личном  │
  │ глобал │   │ расписании      │
  └────┬───┘   └────┬───────────┘
       │            │
  ┌────┴─────┐      │
  │ Уроки     │      │
  │ найдены?  │      │
  └────┬─────┘      │
     Y │ N          │
      ▼ ▼           │
      ●──────┐      │
             │      │
             └──────┘
             │
             ▼
    ┌──────────────────┐
    │ Вернуть уроки +  │
    │ тип расписания   │
    └──────────────────┘
             │
             ▼
           END
```

**Пошаговый пример:**

```python
# Сценарий: Ученик Иван, класс 10А, день 1 (Пн)
student = Student.objects.get(telegram_id=123)
# student.use_global = True
# student.grade = 10
# student.letter = 'А'

lessons, lesson_type = get_student_lessons(student, 1)

# ШАГ 1: Проверяем условие
if student.use_global and student.grade and student.letter:
    # True and True and True = True
    # Входим в блок if
    
    # ШАГ 2: Ищем в GlobalLesson
    lessons = GlobalLesson.objects.filter(
        grade=10,
        letter='А',
        day=1
    ).order_by('number')
    
    # SQL: SELECT * FROM bot_globallesson 
    #      WHERE grade=10 AND letter='А' AND day=1
    #      ORDER BY number
    
    # ШАГ 3: Проверяем, нашли ли что-то
    if lessons.exists():  # Если нашли уроки
        return lessons, 'global'
        # ✅ ВЕРНУЛИ глобальное расписание

# Если условие не выполнено или уроков не найдено:
lessons = PersonalLesson.objects.filter(
    student=student,
    day=1
).order_by('number')
return lessons, 'personal'
```

**Результат в БД:**
```
─ GlobalLesson (классные уроки 10А в понедельник):
  ├─ 1. Математика
  ├─ 2. Русский язык
  └─ 3. История

─ PersonalLesson (уроки Ивана в понедельник):
  ├─ 1. Физика
  └─ 2. Английский

─ get_student_lessons(иван, 1):
  ├─ Если use_global=True → вернёт GlobalLesson
  └─ Если use_global=False → вернёт PersonalLesson
```

---

### Функция 5: `get_next_lesson()` (Строки 64-77)

```python
def get_next_lesson(student, current_time):
    today_num = current_time.isoweekday()
    if today_num > 5:
        return None, None
    
    lessons, lesson_type = get_student_lessons(student, today_num)
    current_time_str = current_time.strftime("%H:%M")
    
    for lesson in lessons:
        start_time, _ = get_lesson_time(lesson.number)
        if start_time > current_time_str:
            return lesson, start_time
    
    return None, None
```

**Что делает?** Находит СЛЕДУЮЩИЙ урок, который ещё не начался

**Понимание `isoweekday()`:**
```python
# ISO недельный день (по стандарту ISO 8601):
now = datetime.now(MSK_TZ)
now.isoweekday()
│
├─ 1 = Понедельник (Monday)
├─ 2 = Вторник (Tuesday)
├─ 3 = Среда (Wednesday)
├─ 4 = Четверг (Thursday)
├─ 5 = Пятница (Friday)
├─ 6 = Суббота (Saturday)
└─ 7 = Воскресенье (Sunday)

# Противоположность - weekday():
# 0 = Понедельник, 6 = Воскресенье (по стандарту Python)
```

**Почему проверяем `today_num > 5`?**
```python
if today_num > 5:  # Если суббота (6) или воскресенье (7)
    return None, None  # Уроков нет
```

**Пошаговый пример:**

```python
# Сценарий: Сегодня среда (день 3), текущее время 10:45
student = Student(name='Иван', grade=10, letter='А')
current_time = datetime(2026, 2, 18, 10, 45)  # 10:45

lessons, _ = get_student_lessons(student, 3)
# lessons = [
#     Урок(1, 'Математика'),      # 08:00-08:40
#     Урок(2, 'Русский'),          # 08:50-09:30
#     Урок(3, 'Английский'),       # 09:50-10:30
#     Урок(4, 'История'),          # 10:50-11:30
#     Урок(5, 'Физика'),           # 11:40-12:20
# ]

current_time_str = "10:45"

# Итерируем по урокам:
for lesson in lessons:
    start_time, _ = get_lesson_time(lesson.number)
    
    # Итерация 1: start_time = "08:00"
    # "08:00" > "10:45" → False (урок уже прошёл)
    
    # Итерация 2: start_time = "08:50"
    # "08:50" > "10:45" → False (урок уже прошёл)
    
    # Итерация 3: start_time = "09:50"
    # "09:50" > "10:45" → False (урок уже прошёл)
    
    # Итерация 4: start_time = "10:50"
    # "10:50" > "10:45" → True! ✅
    # return Урок(4, 'История'), "10:50"
```

**Результат:** Следующий урок - История в 10:50

---

# КЛАВИАТУРЫ

## 📱 Что такое клавиатуры в Telegram боте?

**Обычная клавиатура (ReplyKeyboardMarkup):**
```
Когда я нажимаю кнопку, она заменяет текстовое поле клавиатуры:

┌─────────────────────────────────────┐
│ 📅 Сегодня  │  📆 Завтра          │
├─────────────────────────────────────┤
│ 📚 Неделя  │  ⏰ Следующий урок  │
├─────────────────────────────────────┤
│ ⚙️ Настройки  │  ℹ️ Информация      │
└─────────────────────────────────────┘

Когда я нажимаю "📅 Сегодня":
- Текстовое поле принимает это как сообщение "📅 Сегодня"
- Бот получает message.text == "📅 Сегодня"
```

**Встроенная клавиатура (InlineKeyboardMarkup):**
```
Когда я нажимаю кнопку, она отправляет callback (не текст):

┌─────────────────────────────────┐
│ Выбери класс:                  │
├─────────────────────────────────┤
│ ┌────┬────┬────┬────────────┐  │
│ │ 1  │ 2  │ 3  │ ... │ 11   │  │
│ └────┴────┴────┴────────────┘  │
└─────────────────────────────────┘

Когда я нажимаю "1":
- Отправляется callback с данными: callback_data="grade_1"
- Бот получает: call.data == "grade_1"
```

### Функция: `get_main_keyboard()` (Строки 80-89)

```python
def get_main_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = telebot.types.KeyboardButton("📅 Сегодня")
    btn2 = telebot.types.KeyboardButton("📆 Завтра")
    btn3 = telebot.types.KeyboardButton("📚 Неделя")
    btn4 = telebot.types.KeyboardButton("⏰ Следующий урок")
    btn5 = telebot.types.KeyboardButton("⚙️ Настройки")
    btn6 = telebot.types.KeyboardButton("ℹ️ Информация")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup
```

**Пошаговый разбор:**

```python
# Шаг 1: Создаём объект клавиатуры
markup = telebot.types.ReplyKeyboardMarkup(
    resize_keyboard=True,  # Кнопки подстраиваются под экран
    row_width=2            # 2 кнопки в одной строке
)

# Шаг 2: Создаём кнопки
btn1 = telebot.types.KeyboardButton("📅 Сегодня")
btn2 = telebot.types.KeyboardButton("📆 Завтра")
# ... и т.д.

# Шаг 3: Добавляем кнопки в клавиатуру
markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
# row_width=2 означает:
# Строка 1: btn1, btn2     (2 кнопки)
# Строка 2: btn3, btn4     (2 кнопки)
# Строка 3: btn5, btn6     (2 кнопки)

# Шаг 4: Возвращаем клавиатуру
return markup
```

**Результат на экране:**
```
┌──────────────┬──────────────┐
│ 📅 Сегодня   │ 📆 Завтра    │
├──────────────┼──────────────┤
│ 📚 Неделя    │ ⏰ Сл. урок  │
├──────────────┼──────────────┤
│ ⚙️ Настройки │ ℹ️ Информ.   │
└──────────────┴──────────────┘
```

---

### Функция: `get_settings_keyboard()` (Строки 92-98)

```python
def get_settings_keyboard(student):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = telebot.types.KeyboardButton("🔄 Сменить класс")
    btn2 = telebot.types.KeyboardButton("📋 Тип расписания")
    btn3 = telebot.types.KeyboardButton("🔙 Назад в меню")
    markup.add(btn1, btn2, btn3)
    return markup
```

**Отличие:**
```python
row_width=1  # 1 кнопка в строке (вертикально)

Результат:
┌────────────────────┐
│ 🔄 Сменить класс   │
├────────────────────┤
│ 📋 Тип расписания  │
├────────────────────┤
│ 🔙 Назад в меню    │
└────────────────────┘
```

---

### Функция: `get_back_keyboard()` (Строки 101-104)

```python
def get_back_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("🔙 Назад в меню"))
    return markup
```

**Упрощённая версия:** только одна кнопка для возврата в меню

---

# ОБРАБОТЧИКИ КОМАНД

## 🤖 Как работают обработчики?

```python
@bot.message_handler(commands=['start'])
def start(message):
    # Эта функция вызывается при /start
    ...
```

**Механизм:**
```
Пользователь пишет /start
         │
         ▼
Telegram сервер отправляет данные нашему боту (HTTP запрос)
         │
         ▼
Bot получает запрос
         │
         ▼
Проверяет декораторы (@bot.message_handler):
├─ Это команда /start? ✅ Вызываем start(message)
├─ Это текст "📅 Сегодня"? ✅ Вызываем handle_today(message)
├─ Это callback нажатия кнопки? ✅ Вызываем handle_callback(call)
└─ Это что-то другое? ❌ Игнорируем
```

---

## 🚀 Обработчик команды /start (Строки 107-137)

```python
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    name = message.from_user.first_name or "Ученик"
    
    student, created = Student.objects.get_or_create(
        telegram_id=user_id,
        defaults={'name': name}
    )
    
    if created or not student.grade:
        markup = telebot.types.InlineKeyboardMarkup(row_width=4)
        for g in range(1, 12):
            markup.add(telebot.types.InlineKeyboardButton(
                str(g), 
                callback_data=f"grade_{g}"
            ))
        
        bot.send_message(
            message.chat.id,
            "🎓 *Добро пожаловать в бот расписания!*\n\n"
            "Я помогу тебе:\n"
            "✅ Всегда знать своё расписание\n"
            "✅ Не пропускать уроки\n"
            "✅ Получать напоминания\n\n"
            "📚 *Для начала выбери свой класс:*",
            parse_mode='Markdown',
            reply_markup=markup
        )
    else:
        show_main_menu(message, student)
```

### 📝 Детальный разбор:

#### **Строка 108: `user_id = message.chat.id`**

```python
user_id = message.chat.id
```

**Что это?** Уникальный идентификатор чата (ID пользователя в Telegram)

**Структура объекта `message`:**
```python
message = {
    chat: {
        id: 123456789,      # ← Это user_id
        type: 'private'
    },
    from_user: {
        id: 123456789,
        first_name: 'Иван',
        last_name: 'Петров'
    },
    text: '/start',
    date: 1708169445
}
```

#### **Строка 109: `name = message.from_user.first_name or "Ученик"`**

```python
name = message.from_user.first_name or "Ученик"
```

**Логика (или operator):**
```python
# Если first_name существует и не пусто:
message.from_user.first_name = "Иван"
name = "Иван" or "Ученик"  # Используется "Иван"

# Если first_name пусто:
message.from_user.first_name = None
name = None or "Ученик"  # Используется "Ученик"
```

#### **Строки 111-114: Создание или получение ученика**

```python
student, created = Student.objects.get_or_create(
    telegram_id=user_id,
    defaults={'name': name}
)
```

**Что это?** Django метод для "получить или создать"

**Пошаговая логика:**

```python
# Сценарий 1: Новый пользователь
user_id = 123456789
# Проверяем: есть ли Student с telegram_id=123456789?
# НЕТ → Создаём новую запись

student = Student.objects.create(
    telegram_id=123456789,
    name='Иван'
)
created = True  # Флаг: мы создали новую запись

# Сценарий 2: Существующий пользователь
# Проверяем: есть ли Student с telegram_id=123456789?
# ДА → Возвращаем существующую запись

student = Student.objects.get(telegram_id=123456789)
created = False  # Флаг: запись уже существовала
```

**Результат в БД:**
```
ДО (таблица пуста):
┌────────┬──────┐
│ tel_id │ name │
├────────┼──────┤
└────────┴──────┘

ПОСЛЕ первого /start:
┌────────────────┬───────┐
│ telegram_id    │ name  │
├────────────────┼───────┤
│ 123456789      │ Иван  │
├────────────────┼───────┤
│ grade: NULL    │       │
│ letter: NULL   │       │
│ use_global: T  │       │
└────────────────┴───────┘

ПОСЛЕ второго /start (того же пользователя):
(ничего не меняется, просто возвращается существующая запись)
```

#### **Строки 117-123: Проверка условия и создание клавиатуры**

```python
if created or not student.grade:
    # Если это новый пользователь ИЛИ у него не задан класс
    # → Показываем выбор класса
```

**Когда это верно?**
```
created = True      → Новый пользователь
created = False, grade = NULL → Существующий, но без класса
created = False, grade = 10   → Существующий с классом → НЕ входим в if
```

**Создание инлайн-клавиатуры:**
```python
markup = telebot.types.InlineKeyboardMarkup(row_width=4)
# row_width=4 → 4 кнопки в строке

for g in range(1, 12):
    # range(1, 12) = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    markup.add(telebot.types.InlineKeyboardButton(
        str(g),              # Текст кнопки: "1", "2", ..., "11"
        callback_data=f"grade_{g}"  # Данные при нажатии: "grade_1", "grade_2", ...
    ))
```

**Результат на экране:**
```
┌────┬────┬────┬────────────┐
│ 1  │ 2  │ 3  │ 4          │
├────┼────┼────┼────────────┤
│ 5  │ 6  │ 7  │ 8          │
├────┼────┼────┼────────────┤
│ 9  │ 10 │ 11 │            │
└────┴────┴────┴────────────┘
```

#### **Строки 125-135: Отправка приветственного сообщения**

```python
bot.send_message(
    message.chat.id,
    "🎓 *Добро пожаловать в бот расписания!*\n\n"
    "Я помогу тебе:\n"
    "✅ Всегда знать своё расписание\n"
    "✅ Не пропускать уроки\n"
    "✅ Получать напоминания\n\n"
    "📚 *Для начала выбери свой класс:*",
    parse_mode='Markdown',
    reply_markup=markup
)
```

**Параметры `send_message`:**
- **chat_id**: куда отправить (ID пользователя)
- **text**: текст сообщения
- **parse_mode='Markdown'**: 
  ```
  *текст* → ЖИРНЫЙ
  _текст_ → Курсив
  `код`   → Моноширинный шрифт
  ```
- **reply_markup**: какую клавиатуру прикрепить

**Результат:**
```
Пользователю приходит сообщение:

🎓 Добро пожаловать в бот расписания!

Я помогу тебе:
✅ Всегда знать своё расписание
✅ Не пропускать уроки
✅ Получать напоминания

📚 Для начала выбери свой класс:

┌──┬──┬──┬──────┐
│1 │2 │3 │4 ... │
└──┴──┴──┴──────┘
```

---

## 🏠 Функция `show_main_menu()` (Строки 140-167)

```python
def show_main_menu(message, student):
    class_info = f"{student.grade}{student.letter}"
    now = get_current_lesson_time()
    next_lesson, next_time = get_next_lesson(student, now)
    
    welcome_text = (
        f"🏠 *Главное меню*\n\n"
        f"👤 *Ученик:* {student.name}\n"
        f"🎓 *Класс:* {class_info}\n"
        f"📋 *Расписание:* {'🌍 Глобальное' if student.use_global else '👤 Личное'}\n"
    )
    
    if next_lesson:
        welcome_text += f"\n⏰ *Следующий урок:*\n📚 {next_lesson.subject} в {next_time}"
    else:
        if now.isoweekday() > 5:
            welcome_text += "\n\n🎉 *Выходной день!*"
        else:
            welcome_text += "\n\n✨ *Уроков больше нет*"
    
    welcome_text += "\n\n*Выбери действие:*"
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )
```

**Что это?** Главное меню бота с информацией о ученике и следующем уроке

**Пошаговый разбор:**

```python
# Шаг 1: Формируем информацию о классе
class_info = f"{student.grade}{student.letter}"
# Если grade=10, letter='А' → class_info = "10А"

# Шаг 2: Получаем текущее время
now = get_current_lesson_time()

# Шаг 3: Находим следующий урок
next_lesson, next_time = get_next_lesson(student, now)
# next_lesson = Урок object или None
# next_time = "10:50" или None

# Шаг 4: Начинаем формировать текст
welcome_text = (
    f"🏠 *Главное меню*\n\n"
    f"👤 *Ученик:* Иван\n"
    f"🎓 *Класс:* 10А\n"
    f"📋 *Расписание:* 🌍 Глобальное\n"
)

# Шаг 5: Добавляем информацию о следующем уроке
if next_lesson:  # Если урок найден
    welcome_text += f"\n⏰ *Следующий урок:*\n📚 История в 10:50"
else:  # Если урока нет
    if now.isoweekday() > 5:  # Выходной?
        welcome_text += "\n\n🎉 *Выходной день!*"
    else:  # Уроки закончились
        welcome_text += "\n\n✨ *Уроков больше нет*"

# Шаг 6: Отправляем сообщение
bot.send_message(message.chat.id, welcome_text, ...)
```

**Пример результата на экране:**

```
🏠 Главное меню

👤 Ученик: Иван
🎓 Класс: 10А
📋 Расписание: 🌍 Глобальное

⏰ Следующий урок:
📚 История в 10:50

Выбери действие:

┌──────────────┬──────────────┐
│ 📅 Сегодня   │ 📆 Завтра    │
├──────────────┼──────────────┤
│ 📚 Неделя    │ ⏰ Сл. урок  │
├──────────────┼──────────────┤
│ ⚙️ Настройки │ ℹ️ Информ.   │
└──────────────┴──────────────┘
```

---

## 📅 Обработчик "Сегодня" (Строки 180-254)

```python
@bot.message_handler(func=lambda message: message.text == "📅 Сегодня")
def handle_today(message):
    user_id = message.chat.id
    student = Student.objects.get(telegram_id=user_id)
    
    today_num = get_current_lesson_time().isoweekday()
    
    if today_num > 5:
        # Выходной
        bot.send_message(message.chat.id, "🎉 *Сегодня выходной!*", ...)
        return
    
    lessons, lesson_type = get_student_lessons(student, today_num)
    
    if not lessons:
        # Расписание не найдено
        # Показываем сообщение и варианты (создать личное/написать админу)
        ...
        return
    
    # Формируем и отправляем расписание на день
    days = {1: "ПОНЕДЕЛЬНИК", 2: "ВТОРНИК", ...}
    source = "🌍 Глобальное" if lesson_type == 'global' else "👤 Личное"
    
    text = f"📅 *{days[today_num]}*\n"
    text += f"📋 {source} расписание\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    now = get_current_lesson_time().strftime("%H:%M")
    
    for lesson in lessons:
        start, end = get_lesson_time(lesson.number)
        
        # Определяем статус урока
        if start > now:
            status = " ⏳"  # Еще не начался
        elif end < now:
            status = " ✅"  # Уже прошёл
        else:
            status = " 🔴"  # Идёт прямо сейчас
        
        text += f"*{lesson.number}. {lesson.subject}*{status}\n"
        text += f"   ⏰ {start} - {end}\n\n"
    
    bot.send_message(message.chat.id, text, ...)
```

**Логика статуса урока:**

```
Урок начинается в 10:50, заканчивается в 11:30

1. Текущее время 09:00
   ├─ start (10:50) > now (09:00) → True
   └─ status = " ⏳" (ещё не начался)

2. Текущее время 11:00 (урок идёт)
   ├─ start (10:50) > now (11:00) → False
   ├─ end (11:30) < now (11:00) → False
   └─ status = " 🔴" (идёт сейчас!)

3. Текущее время 12:00
   ├─ start (10:50) > now (12:00) → False
   ├─ end (11:30) < now (12:00) → True
   └─ status = " ✅" (уже прошёл)
```

**Пример результата:**
```
📅 ПОНЕДЕЛЬНИК
📋 🌍 Глобальное расписание
━━━━━━━━━━━━━━━━━━━━

1. Математика ⏳
   ⏰ 08:00 - 08:40

2. Русский язык ✅
   ⏰ 08:50 - 09:30

3. Английский 🔴
   ⏰ 09:50 - 10:30

4. История ⏳
   ⏰ 10:50 - 11:30
```

---

## ⏰ Обработчик "Следующий урок" (Строки 343-377)

```python
@bot.message_handler(func=lambda message: message.text == "⏰ Следующий урок")
def next_lesson_command(message):
    user_id = message.chat.id
    student = Student.objects.get(telegram_id=user_id)
    
    now = get_current_lesson_time()
    next_lesson, next_time = get_next_lesson(student, now)
    
    if next_lesson:
        start, end = get_lesson_time(next_lesson.number)
        time_until = datetime.strptime(next_time, "%H:%M") - datetime.strptime(now.strftime("%H:%M"), "%H:%M")
        minutes_until = int(time_until.total_seconds() / 60)
        
        text = (
            f"⏰ *Следующий урок*\n\n"
            f"📚 *{next_lesson.subject}*\n"
            f"🔢 Урок №{next_lesson.number}\n"
            f"⏱️ {start} - {end}\n"
            f"⌛️ До начала: {minutes_until} мин.\n"
        )
        
        if minutes_until <= REMINDER_MINUTES:
            text += f"\n⚠️ *Урок начнётся совсем скоро!*"
    else:
        if now.isoweekday() > 5:
            text = "🎉 *Сегодня выходной!*"
        else:
            text = "✨ *На сегодня все уроки закончились*"
    
    bot.send_message(message.chat.id, text, ...)
```

### 🔢 Вычисление времени до урока:

```python
# Сценарий: текущее время 10:45, следующий урок в 10:50

next_time = "10:50"
now_str = "10:45"

# Преобразуем в объекты time для сравнения
next_time_obj = datetime.strptime("10:50", "%H:%M")
now_obj = datetime.strptime("10:45", "%H:%M")

# Вычитаем и получаем разницу
time_until = next_time_obj - now_obj
# time_until = timedelta(seconds=300)

# Преобразуем в минуты
minutes_until = int(time_until.total_seconds() / 60)
# minutes_until = 300 / 60 = 5 минут

# Выводим
text = f"⌛️ До начала: 5 мин.\n"

if minutes_until <= 10:  # Менее 10 минут?
    text += "\n⚠️ *Урок начнётся совсем скоро!*"
```

---

## ⚙️ Обработчик callback кнопок (Строки 464-671)

```python
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.message.chat.id
    student = Student.objects.get(telegram_id=user_id)
    
    # Множество условий для разных кнопок
    if call.data.startswith('grade_'):
        ...
    elif call.data.startswith('letter_'):
        ...
    elif call.data == 'use_global':
        ...
    # и т.д.
```

**Декоратор `@bot.callback_query_handler(func=lambda call: True)`:**
- Обрабатывает нажатия на ЛЮБЫЕ встроенные кнопки
- `func=lambda call: True` значит "для всех колбеков"
- Можно фильтровать: `func=lambda call: call.data == 'use_global'`

### Пример: Выбор класса

```python
if call.data.startswith('grade_'):
    # Пользователь нажал кнопку класса (1-11)
    
    # Извлекаем номер класса из callback_data
    grade = int(call.data.split('_')[1])
    # call.data = "grade_10"
    # call.data.split('_') = ["grade", "10"]
    # int("10") = 10
    
    # Сохраняем в временное хранилище
    temp_data[user_id] = {'grade': grade}
    
    # Создаём следующую клавиатуру для выбора буквы
    markup = telebot.types.InlineKeyboardMarkup(row_width=4)
    for letter in ['А', 'Б', 'В', 'Г']:
        markup.add(telebot.types.InlineKeyboardButton(
            letter,
            callback_data=f"letter_{letter}"
        ))
    
    # Обновляем существующее сообщение (не создаём новое)
    bot.edit_message_text(
        f"📚 *Класс {grade}*\n\nТеперь выбери букву:",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=markup
    )
```

**Диаграмма взаимодействия:**
```
Пользователь нажимает "10"
         │
         ▼
callback_data = "grade_10" отправляется боту
         │
         ▼
handle_callback(call) вызывается
         │
         ▼
if call.data.startswith('grade_'):  ✅ True
         │
         ▼
grade = int("10") = 10
temp_data[user_id] = {'grade': 10}
         │
         ▼
Создаём клавиатуру с буквами
         │
         ▼
Обновляем сообщение (edit_message_text)
         │
         ▼
На экране:
┌────────────────────┐
│ 📚 Класс 10        │
│                    │
│ Теперь выбери букву│
│                    │
│ ┌──┬──┬──┬──────┐ │
│ │А │Б │В │Г     │ │
│ └──┴──┴──┴──────┘ │
└────────────────────┘
```

### Пример: Сохранение класса

```python
elif call.data.startswith('letter_'):
    # Пользователь выбрал букву
    
    letter = call.data.split('_')[1]  # "А"
    grade = temp_data[user_id]['grade']  # 10 (из временного хранилища)
    
    # Обновляем ученика в БД
    student.grade = grade
    student.letter = letter
    student.save()
    
    # Отправляем подтверждение
    bot.edit_message_text(
        f"✅ *Класс успешно установлен!*\n\n📚 Твой класс: *10А*",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )
    
    # Показываем главное меню
    show_main_menu(call.message, student)
    
    # Удаляем временные данные
    del temp_data[user_id]
```

**Результат в БД:**
```
ДО:
┌────────────────┬───────┬────────┬──────────┐
│ telegram_id    │ name  │ grade  │ letter   │
├────────────────┼───────┼────────┼──────────┤
│ 123456789      │ Иван  │ NULL   │ NULL     │
└────────────────┴───────┴────────┴──────────┘

ПОСЛЕ:
┌────────────────┬───────┬────────┬──────────┐
│ telegram_id    │ name  │ grade  │ letter   │
├────────────────┼───────┼────────┼──────────┤
│ 123456789      │ Иван  │ 10     │ А        │
└────────────────┴───────┴────────┴──────────┘
```

---

## 📝 Создание личного расписания (Строки 674-754)

```python
@bot.message_handler(func=lambda message: message.chat.id in temp_data)
def handle_add_personal(message):
    user_id = message.chat.id
    data = temp_data[user_id]
    
    if data.get('action') != 'add_personal':
        return
    
    if data['step'] == 'day':
        # Пользователь вводит день (1-5)
        try:
            day = int(message.text.strip())
            
            if day < 1 or day > 5:
                bot.reply_to(message, "❌ День должен быть от 1 до 5")
                return
            
            data['day'] = day
            data['step'] = 'subjects'
            
            bot.send_message(
                user_id,
                f"✅ День: *Понедельник*\n\n"
                f"📝 Теперь введи предметы\n\n"
                f"*Каждый с новой строки!*",
                parse_mode='Markdown'
            )
        
        except ValueError:
            bot.reply_to(message, "❌ Нужно ввести число от 1 до 5")
    
    elif data['step'] == 'subjects':
        # Пользователь вводит предметы
        subjects = [s.strip() for s in message.text.split('\n') if s.strip()]
        
        if not subjects:
            bot.send_message(user_id, "❌ Нет предметов!")
            return
        
        student = Student.objects.get(telegram_id=user_id)
        day = data['day']
        
        # Удаляем старое расписание на этот день
        PersonalLesson.objects.filter(student=student, day=day).delete()
        
        # Добавляем новые уроки
        for i, subject in enumerate(subjects, start=1):
            PersonalLesson.objects.create(
                student=student,
                day=day,
                number=i,
                subject=subject
            )
        
        # Формируем подтверждение
        confirmation = f"✅ *Личное расписание создано!*\n\n"
        confirmation += f"📅 Понедельник\n"
        confirmation += f"📚 Добавлено: {len(subjects)} уроков\n\n"
        
        for i, subject in enumerate(subjects, start=1):
            start_time, end_time = get_lesson_time(i)
            confirmation += f"{i}. {subject} ({start_time}-{end_time})\n"
        
        confirmation += "\n💡 Переключись на личное в настройках!"
        
        bot.send_message(user_id, confirmation, ...)
        
        # Удаляем временные данные
        del temp_data[user_id]
```

### 🎯 Алгоритм создания личного расписания:

**Шаг 1: Выбор дня**
```
Пользователь: "1" (Понедельник)
↓
Проверка: 1 <= день <= 5? ✅
↓
Сохранение: temp_data[user_id] = {'action': 'add_personal', 'step': 'subjects', 'day': 1}
↓
Просим ввести предметы
```

**Шаг 2: Ввод предметов**
```
Пользователь пишет:
Русский язык
Математика
История

↓
Разбиваем по строкам: ['Русский язык', 'Математика', 'История']
↓
Создаём PersonalLesson для каждого:
- PersonalLesson(student=Иван, day=1, number=1, subject='Русский язык')
- PersonalLesson(student=Иван, day=1, number=2, subject='Математика')
- PersonalLesson(student=Иван, day=1, number=3, subject='История')
↓
Удаляем временные данные
```

**Результат в БД:**
```
PersonalLesson таблица:
┌────────────┬──────┬────────┬────────────────┐
│ student_id │ day  │ number │ subject        │
├────────────┼──────┼────────┼────────────────┤
│ 1          │ 1    │ 1      │ Русский язык   │
│ 1          │ 1    │ 2      │ Математика     │
│ 1          │ 1    │ 3      │ История        │
└────────────┴──────┴────────┴────────────────┘
```

---

# ФОНОВЫЕ ПОТОКИ

## 🔄 Что такое фоновые потоки?

Основной поток: обрабатывает команды пользователей
```
Пользователь пишет /start → Обработчик вызывается → Ответ отправляется
```

Фоновый поток: работает одновременно, независимо
```
Работает 24/7 → Проверяет время → Отправляет напоминания/рассылки
```

**Без потоков:**
```
Bot.polling()  ← Основной цикл (ждёт сообщений)
    ↓
Если фоновая задача заблокирует, весь бот застынет!
```

**С потоками:**
```
                    Основной поток
                    ├─ bot.polling()
                    
     Поток 1                      Поток 2
     ├─ reminder_checker()        ├─ morning_sender()
```

---

## 🔔 Функция `reminder_checker()` (Строки 757-803)

```python
def reminder_checker():
    print("🔔 Поток напоминаний запущен")
    
    while True:
        try:
            now = get_current_lesson_time()
            today_num = now.isoweekday()
            
            if today_num <= 5:  # Только ПН-ПТ
                students = Student.objects.all()
                
                for student in students:
                    try:
                        lessons, _ = get_student_lessons(student, today_num)
                        
                        for lesson in lessons:
                            start_time_str, _ = get_lesson_time(lesson.number)
                            start_time = datetime.strptime(start_time_str, "%H:%M").time()
                            reminder_time = (
                                datetime.combine(datetime.today(), start_time) - 
                                timedelta(minutes=REMINDER_MINUTES)
                            ).time()
                            
                            current_time = now.time()
                            
                            if (current_time.hour == reminder_time.hour and 
                                current_time.minute == reminder_time.minute):
                                
                                text = (
                                    f"⚠️ *НАПОМИНАНИЕ!*\n\n"
                                    f"⏰ Через *{REMINDER_MINUTES} минут* урок:\n\n"
                                    f"📚 *{lesson.number}. {lesson.subject}*\n"
                                    f"🕐 Начало: {start_time_str}\n\n"
                                    f"💼 Пора собираться!"
                                )
                                
                                bot.send_message(student.telegram_id, text, parse_mode='Markdown')
                                print(f"✅ Напоминание: {student.name} - {lesson.subject}")
                    
                    except Exception as e:
                        print(f"❌ Ошибка для {student.telegram_id}: {e}")
            
            time.sleep(30)
        
        except Exception as e:
            print(f"❌ Ошибка в reminder_checker: {e}")
            time.sleep(60)
```

### 📊 Пошаговый разбор логики:

#### **Основной цикл**

```python
while True:
    # Работает бесконечно, пока программа запущена
    
    now = get_current_lesson_time()  # Текущее время в Москве
    today_num = now.isoweekday()     # День недели (1-7)
    
    if today_num <= 5:  # Только ПН-ПТ
        # Работаем только в будни, в выходные пропускаем
        ...
    
    time.sleep(30)  # Пауза 30 секунд перед следующей проверкой
```

**Почему 30 секунд?**
```
- Если 10 минут: пропустим много временных точек
- Если 1 секунда: перегрузим сервер частыми проверками
- 30 секунд: хороший баланс
```

#### **Расчёт времени напоминания**

Это самая сложная часть:

```python
start_time_str = "09:50"  # Строка формата "ЧЧ:ММ"
start_time = datetime.strptime(start_time_str, "%H:%M").time()
# start_time = datetime.time(9, 50)

# Создаём объект datetime на сегодняшний день с этим временем
start_datetime = datetime.combine(datetime.today(), start_time)
# start_datetime = datetime.datetime(2026, 2, 18, 9, 50)

# Вычитаем 10 минут
reminder_datetime = start_datetime - timedelta(minutes=10)
# reminder_datetime = datetime.datetime(2026, 2, 18, 9, 40)

# Конвертируем обратно в time
reminder_time = reminder_datetime.time()
# reminder_time = datetime.time(9, 40)
```

**Визуально:**
```
Урок начинается      →  09:50
                        │
            Напоминание отправляется за 10 минут
                        │
                        ▼
                       09:40 ← reminder_time
```

#### **Проверка, пришло ли время напоминания**

```python
current_time = now.time()  # Текущее время (например, 09:40:15)
reminder_time.hour = 9
reminder_time.minute = 40

if (current_time.hour == reminder_time.hour and 
    current_time.minute == reminder_time.minute):
    # Если часы совпадают И минуты совпадают
    # → Отправляем напоминание!
```

**Пример:**
```
current_time = 09:40:15 (9 часов, 40 минут, 15 секунд)
reminder_time = 09:40 (9 часов, 40 минут)

current_time.hour (9) == reminder_time.hour (9) → True
current_time.minute (40) == reminder_time.minute (40) → True
→ ✅ Отправляем напоминание!
```

#### **Отправка напоминания**

```python
text = (
    f"⚠️ *НАПОМИНАНИЕ!*\n\n"
    f"⏰ Через *10 минут* урок:\n\n"
    f"📚 *2. Русский язык*\n"
    f"🕐 Начало: 09:50\n\n"
    f"💼 Пора собираться!"
)

bot.send_message(student.telegram_id, text, parse_mode='Markdown')
```

**Результат на экране:**
```
⚠️ НАПОМИНАНИЕ!

⏰ Через 10 минут урок:

📚 2. Русский язык
🕐 Начало: 09:50

💼 Пора собираться!
```

---

## 📬 Функция `morning_sender()` (Строки 806-847)

```python
def morning_sender():
    print("📬 Поток рассылки запущен")
    
    while True:
        try:
            now = get_current_lesson_time()
            
            if now.hour == 6 and now.minute == 30:
                # В 6:30 утра отправляем расписание
                students = Student.objects.all()
                today_num = now.isoweekday()
                
                if today_num <= 5:  # Только в будни
                    for student in students:
                        try:
                            lessons, lesson_type = get_student_lessons(student, today_num)
                            
                            if lessons:
                                days = {1: "ПОНЕДЕЛЬНИК", 2: "ВТОРНИК", ...}
                                source = "🌍" if lesson_type == 'global' else "👤"
                                
                                text = f"{source} *Доброе утро, {student.name}!*\n\n"
                                text += f"📅 *{days[today_num]}*\n"
                                text += "━━━━━━━━━━━━━━━━━━━━\n\n"
                                
                                for lesson in lessons:
                                    start, end = get_lesson_time(lesson.number)
                                    text += f"*{lesson.number}. {lesson.subject}*\n"
                                    text += f"   ⏰ {start} - {end}\n\n"
                                
                                text += "💪 *Удачного дня!*"
                                
                                bot.send_message(student.telegram_id, text, ...)
                                print(f"✅ Рассылка: {student.name}")
                        
                        except Exception as e:
                            print(f"❌ Ошибка: {e}")
            
            time.sleep(60)
        
        except Exception as e:
            print(f"❌ Ошибка в morning_sender: {e}")
            time.sleep(60)
```

### 🌅 Разбор утренней рассылки:

**Когда работает?**
```
Каждую секунду проверяем:
├─ now.hour == 6 AND now.minute == 30?
│
├─ 06:00 → Нет (только час совпадает)
├─ 06:30 → ДА! ✅ Отправляем рассылку
├─ 06:31 → Нет (минута не совпадает)
└─ 07:00 → Нет
```

**Что отправляется?**
```
📬 Доброе утро, Иван!

📅 ПОНЕДЕЛЬНИК
━━━━━━━━━━━━━━━━━━━━

1. Математика
   ⏰ 08:00 - 08:40

2. Русский язык
   ⏰ 08:50 - 09:30

💪 Удачного дня!
```

**Почему каждую секунду, а не один раз в день?**
```
Ненадёжный способ:
├─ Запомнить flag "уже отправили"
├─ Если программа перезагрузилась в 06:31 → пропустим рассылку
└─ ❌ Неправильно

Надёжный способ:
├─ Каждую секунду проверяем время
├─ Если сейчас 06:30 → отправляем
├─ Даже если программа перезагрузилась в 06:30 → отправим
└─ ✅ Правильно
```

---

# ГЛАВНЫЙ ЦИКЛ

## 🚀 Функция `main()` (Строки 850-862)

```python
def main():
    Thread(target=morning_sender, daemon=True).start()
    Thread(target=reminder_checker, daemon=True).start()
    
    print("\n" + "=" * 50)
    print("🤖 БОТ ЗАПУЩЕН!")
    print("=" * 50)
    print("\n✅ Рассылка в 6:30")
    print("✅ Напоминания за 10 минут")
    print("✅ Глобальное и личное расписание")
    print("\n" + "=" * 50 + "\n")
    
    bot.polling(none_stop=True)
```

### 🔄 Как это работает?

```python
# Шаг 1: Запуск фонового потока для утренней рассылки
Thread(target=morning_sender, daemon=True).start()
│
├─ Thread(...) → создаём новый поток
├─ target=morning_sender → функция, которая будет выполняться в потоке
├─ daemon=True → поток завершится, когда завершится основная программа
└─ .start() → запускаем поток

# Шаг 2: Запуск фонового потока для напоминаний
Thread(target=reminder_checker, daemon=True).start()

# Шаг 3: Вывод информации
print(...) 
# Выводит в консоль, что бот запущен

# Шаг 4: Запуск основного цикла
bot.polling(none_stop=True)
│
├─ bot.polling() → подключается к Telegram API
├─ Ждёт входящих сообщений
├─ Вызывает соответствующие обработчики
└─ none_stop=True → работает бесконечно (даже если будут ошибки)
```

### 📊 Диаграмма потоков:

```
         START
           │
           ▼
   ┌───────────────┐
   │  Основной     │
   │   процесс     │
   └───────────────┘
           │
    ┌──────┼──────┐
    │      │      │
    ▼      ▼      ▼
   Поток1 Поток2 Поток3
   (Утро) (Напо) (Polling)
    │      │      │
    │      │      ├─ Слушает входящие сообщения
    │      │      ├─ Вызывает @bot.message_handler
    │      │      └─ Отправляет ответы
    │      │
    │      ├─ Каждые 30 сек проверяет время
    │      ├─ Если час == напоминания → отправляет
    │      └─ (работает 24/7)
    │
    ├─ Каждую минуту проверяет время
    ├─ Если 6:30 → отправляет рассылку
    └─ (работает 24/7)
```

---

## 🎬 Точка входа программы (Строки 865-866)

```python
if __name__ == '__main__':
    main()
```

**Что это?** Стандартный способ в Python для запуска программы

```python
# Если этот файл запущен как основной скрипт:
if __name__ == '__main__':
    main()

# Если этот файл импортирован в другой файл:
# if __name__ == '__main__' → пропускается
```

**Почему это нужно?**
```python
# Сценарий 1: Запускаем как основной скрипт
$ python telegram_bot.py
# __name__ == '__main__' → True
# Вызывается main() → бот запускается

# Сценарий 2: Импортируем функции в другой файл
from bot.telegram_bot import get_lesson_time

# __name__ == 'bot.telegram_bot' → False
# main() не вызывается → избегаем неожиданного запуска бота
```

---

# ПРИМЕРЫ ПОТОКА ДАННЫХ

## 📊 Сценарий 1: Пользователь пишет /start

```
1. TELEGRAM СЕРВЕР
   └─ Пользователь с ID 123456789 отправляет: "/start"

2. НАШ БОТ ПОЛУЧАЕТ ЗАПРОС
   └─ message = {
        chat_id: 123456789,
        text: "/start",
        from_user.first_name: "Иван"
      }

3. МАРШРУТИЗАЦИЯ
   @bot.message_handler(commands=['start'])
   ├─ Проверка: текст == "/start"? → ДА ✅
   └─ Вызываем start(message)

4. ФУНКЦИЯ START ВЫПОЛНЯЕТСЯ
   └─ user_id = 123456789
   └─ name = "Иван"

5. БАЗА ДАННЫХ - ПРОВЕРКА
   Student.objects.get_or_create(telegram_id=123456789, defaults={'name': 'Иван'})
   
   ├─ Есть ли уже ученик с этим ID?
   │  └─ НЕТ → created = True
   │
   └─ Создаём новую запись:
      ┌────────────────┐
      │ Student table  │
      ├────────────────┤
      │ telegram_id: 123456789
      │ name: Иван
      │ grade: NULL (не выбран)
      │ letter: NULL (не выбрана)
      │ use_global: True (по умолчанию)
      └────────────────┘

6. ПРОВЕРКА УСЛОВИЯ
   if created or not student.grade:
   ├─ created = True → ДА ✅
   └─ Показываем выбор класса

7. СОЗДАНИЕ КЛАВИАТУРЫ
   markup = InlineKeyboardMarkup(row_width=4)
   for g in range(1, 12):
      add(InlineKeyboardButton(str(g), callback_data=f"grade_{g}"))
   
   └─ Результат:
      ┌──┬──┬──┬──┬──────┐
      │1 │2 │3 │4 │... 11│
      └──┴──┴──┴──┴──────┘

8. ОТПРАВКА СООБЩЕНИЯ
   bot.send_message(
       123456789,
       "🎓 *Добро пожаловать в бот расписания!*\n...",
       parse_mode='Markdown',
       reply_markup=markup
   )

9. TELEGRAM СЕРВЕР
   └─ Отправляет сообщение с клавиатурой пользователю

10. ЭКРАН ПОЛЬЗОВАТЕЛЯ
    ┌────────────────────────────────┐
    │ 🎓 Добро пожаловать!           │
    │ Я помогу тебе:                 │
    │ ✅ Знать расписание            │
    │ ✅ Не пропускать уроки         │
    │ ✅ Получать напоминания        │
    │                                │
    │ 📚 Выбери свой класс:          │
    │                                │
    │ ┌──┬──┬──┬──────────────┐     │
    │ │1 │2 │3 │4 │... │ 11    │     │
    │ └──┴──┴──┴──────────────┘     │
    └────────────────────────────────┘
```

---

## 📊 Сценарий 2: Пользователь нажимает кнопку "10" (класс)

```
1. TELEGRAM СЕРВЕР
   └─ Пользователь нажимает кнопку "10"
   └─ callback_data = "grade_10" отправляется боту

2. НАШ БОТ ПОЛУЧАЕТ CALLBACK
   call = {
       data: "grade_10",
       message.chat.id: 123456789
   }

3. МАРШРУТИЗАЦИЯ
   @bot.callback_query_handler(func=lambda call: True)
   ├─ Проверка: это какой-то callback? → ДА ✅
   └─ Вызываем handle_callback(call)

4. ФУНКЦИЯ HANDLE_CALLBACK
   user_id = 123456789
   student = Student.objects.get(telegram_id=123456789)
   ├─ Получаем ученика из БД
   └─ student = <Student: Иван>

5. ПРОВЕРКА ТИПА CALLBACK
   if call.data.startswith('grade_'):
   ├─ "grade_10".startswith('grade_') → ДА ✅
   └─ Вызываем обработчик выбора класса

6. ИЗВЛЕЧЕНИЕ НОМЕРА КЛАССА
   grade = int(call.data.split('_')[1])
   ├─ call.data.split('_') = ["grade", "10"]
   ├─ ["grade", "10"][1] = "10"
   ├─ int("10") = 10
   └─ grade = 10

7. СОХРАНЕНИЕ ВРЕМЕННЫХ ДАННЫХ
   temp_data[123456789] = {'grade': 10}
   ├─ Это нужно для следующего шага (выбор буквы)
   └─ Хранится в памяти (не в БД)

8. СОЗДАНИЕ НОВОЙ КЛАВИАТУРЫ
   markup = InlineKeyboardMarkup(row_width=4)
   for letter in ['А', 'Б', 'В', 'Г']:
      add(InlineKeyboardButton(letter, callback_data=f"letter_{letter}"))
   
   └─ Результат:
      ┌──┬──┬──┬──┐
      │А │Б │В │Г │
      └──┴──┴──┴──┘

9. ОБНОВЛЕНИЕ СУЩЕСТВУЮЩЕГО СООБЩЕНИЯ
   bot.edit_message_text(
       "📚 *Класс 10*\n\nТеперь выбери букву:",
       123456789,
       message_id,  # ID предыдущего сообщения
       reply_markup=markup
   )
   
   └─ Сообщение с кнопками класса ЗАМЕНЯЕТСЯ
   └─ на сообщение с кнопками букв
   └─ (не создаётся новое сообщение!)

10. TELEGRAM СЕРВЕР
    └─ Обновляет сообщение на экране пользователя

11. ЭКРАН ПОЛЬЗОВАТЕЛЯ (ИЗМЕНИЛСЯ!)
    ДО:
    ┌──┬──┬──┬──┬──────┐
    │1 │2 │3 │4 │... 11│
    └──┴──┴──┴──┴──────┘
    
    ПОСЛЕ:
    ┌──────────────────┐
    │ 📚 Класс 10      │
    │                  │
    │ Выбери букву:    │
    │                  │
    │ ┌──┬──┬──┬──┐   │
    │ │А │Б │В │Г │   │
    │ └──┴──┴──┴──┘   │
    └──────────────────┘
```

---

## 📊 Сценарий 3: Пользователь нажимает "А" (буква класса)

```
1. TELEGRAM СЕРВЕР
   └─ Пользователь нажимает "А"
   └─ callback_data = "letter_А" отправляется боту

2. ФУНКЦИЯ HANDLE_CALLBACK
   user_id = 123456789
   student = Student.objects.get(telegram_id=123456789)

3. ПРОВЕРКА ТИПА CALLBACK
   if call.data.startswith('letter_'):
   ├─ "letter_А".startswith('letter_') → ДА ✅

4. ИЗВЛЕЧЕНИЕ БУКВЫ
   letter = call.data.split('_')[1]
   ├─ letter = "А"

5. ПОЛУЧЕНИЕ КЛАССА ИЗ ВРЕМЕННЫХ ДАННЫХ
   grade = temp_data[123456789]['grade']
   ├─ grade = 10 (сохранили на предыдущем шаге)

6. ОБНОВЛЕНИЕ УЧЕНИКА В БД
   student.grade = 10
   student.letter = 'А'
   student.save()
   
   └─ БД ДО:
      ┌──────────────┬──────┬────────┬──────────┐
      │ telegram_id  │ name │ grade  │ letter   │
      ├──────────────┼──────┼────────┼──────────┤
      │ 123456789    │ Иван │ NULL   │ NULL     │
      └──────────────┴──────┴────────┴──────────┘
   
   └─ БД ПОСЛЕ:
      ┌──────────────┬──────┬────────┬──────────┐
      │ telegram_id  │ name │ grade  │ letter   │
      ├──────────────┼──────┼────────┼──────────┤
      │ 123456789    │ Иван │ 10     │ А        │
      └──────────────┴──────┴────────┴──────────┘

7. ОТПРАВКА ПОДТВЕРЖДЕНИЯ
   bot.edit_message_text(
       "✅ *Класс успешно установлен!*\n\n📚 Твой класс: *10А*",
       ...
   )

8. ВЫЗОВ ГЛАВНОГО МЕНЮ
   show_main_menu(call.message, student)
   
   ├─ class_info = "10А"
   ├─ now = текущее время
   ├─ next_lesson, next_time = get_next_lesson(student, now)
   │
   └─ Отправляет:
      ┌────────────────────────────┐
      │ 🏠 Главное меню            │
      │                            │
      │ 👤 Ученик: Иван            │
      │ 🎓 Класс: 10А              │
      │ 📋 Расписание: 🌍 Глобальное│
      │                            │
      │ ⏰ Следующий урок:         │
      │ 📚 История в 10:50         │
      │                            │
      │ Выбери действие:           │
      │                            │
      │ ┌──────────┬──────────┐   │
      │ │📅 Сегодня│📆 Завтра │   │
      │ ├──────────┼──────────┤   │
      │ │📚 Неделя │⏰ Сл урок│   │
      │ ├──────────┼──────────┤   │
      │ │⚙️ Настрой│ℹ️ Инфо   │   │
      │ └──────────┴──────────┘   │
      └────────────────────────────┘

9. УДАЛЕНИЕ ВРЕМЕННЫХ ДАННЫХ
   del temp_data[123456789]
   └─ Очищаем память
```

---

## 📊 Сценарий 4: Фоновый поток отправляет напоминание

```
(Это работает независимо от пользовательских действий)

1. ФОНОВЫЙ ПОТОК (reminder_checker)
   └─ Работает в цикле while True
   └─ Каждые 30 секунд проверяет время

2. ПРОВЕРКА ВРЕМЕНИ
   now = datetime.now(MSK_TZ)  # 09:40:15 (9:40 и 15 секунд)
   today_num = 3  # Среда

3. ПРОВЕРКА УСЛОВИЯ
   if today_num <= 5:  # Среда ≤ 5 → ДА ✅

4. ПОЛУЧЕНИЕ ВСЕХ УЧЕНИКОВ
   students = Student.objects.all()
   ├─ students = [<Student: Иван (10А)>, <Student: Мария (9Б)>, ...]

5. ДЛЯ КАЖДОГО УЧЕНИКА
   for student in students:
   
   Пример: Иван (10А)
   
   6. ПОЛУЧЕНИЕ РАСПИСАНИЯ
      lessons, _ = get_student_lessons(иван, 3)  # Среда
      ├─ lessons = [
      │   Урок(1, Математика),
      │   Урок(2, Русский язык),
      │   Урок(3, Английский),  ← УРО К НАЧИНАЕТСЯ ЧЕРЕЗ 10 МИНУТ!
      │   Урок(4, История)
      │ ]

   7. ДЛЯ КАЖДОГО УРОКА
      for lesson in lessons:
      
      Пример: Урок(3, Английский)
      
      8. ПОЛУЧЕНИЕ ВРЕМЕНИ УРОКА
         start_time_str = "09:50"
         start_time = 09:50 (как объект time)
      
      9. РАСЧЁТ ВРЕМЕНИ НАПОМИНАНИЯ
         reminder_time = 09:50 - 10 мин = 09:40
      
      10. ПРОВЕРКА, СОВПАДАЕТ ЛИ ТЕКУЩЕЕ ВРЕМЯ
          current_time = 09:40 (часы и минуты)
          reminder_time = 09:40
          
          if 09:40.hour == 09:40.hour AND 09:40.minute == 09:40.minute:
          ├─ True AND True → ДА! ✅
          └─ ЭТО МОМЕНТ ОТПРАВКИ НАПОМИНАНИЯ!
      
      11. ОТПРАВКА НАПОМИНАНИЯ
          text = (
              "⚠️ *НАПОМИНАНИЕ!*\n\n"
              "⏰ Через *10 минут* урок:\n\n"
              "📚 *3. Английский*\n"
              "🕐 Начало: 09:50\n\n"
              "💼 Пора собираться!"
          )
          
          bot.send_message(123456789, text)

12. TELEGRAM СЕРВЕР
    └─ Отправляет сообщение пользователю

13. ЭКРАН ПОЛЬЗОВАТЕЛЯ
    ┌──────────────────────────┐
    │ ⚠️ НАПОМИНАНИЕ!          │
    │                          │
    │ ⏰ Через 10 минут урок:  │
    │                          │
    │ 📚 3. Английский         │
    │ 🕐 Начало: 09:50         │
    │                          │
    │ 💼 Пора собираться!      │
    └──────────────────────────┘

14. ПОТОК ПРОДОЛЖАЕТ РАБОТУ
    time.sleep(30)
    ├─ Пауза 30 секунд
    └─ Возвращаемся к пункту 1 (циклическая проверка)
```

---

# 🎯 БЫСТРАЯ СПРАВКА

## Команды для запуска

```bash
# Установить зависимости
pip install -r requirements.txt

# Настроить БД
python manage.py migrate

# Запустить бота
python bot/telegram_bot.py
```

## Структура проекта

```
tg_bot--main/
├── manage.py                 # Управление Django
├── requirements.txt          # Зависимости
├── config/
│   ├── settings.py          # Конфигурация Django
│   ├── urls.py              # Маршруты
│   ├── wsgi.py
│   └── asgi.py
├── bot/
│   ├── models.py            # Модели БД (Student, GlobalLesson, ...)
│   ├── admin.py             # Админка Django
│   ├── telegram_bot.py      # ОСНОВНОЙ ФАЙЛ БОТА
│   └── migrations/          # История изменений БД
└── school_schedule_project/  # Копия для документации
```

## Основные классы и функции

| Класс/Функция | Описание |
|---|---|
| `Student` | Модель ученика (telegram_id, name, grade, letter, use_global) |
| `GlobalLesson` | Глобальное расписание для класса |
| `PersonalLesson` | Личное расписание ученика |
| `get_lesson_time(n)` | Получить время начала/конца урока по номеру |
| `get_next_lesson()` | Найти следующий урок |
| `get_student_lessons()` | Получить расписание на день (глобальное или личное) |
| `reminder_checker()` | Фоновый поток для напоминаний |
| `morning_sender()` | Фоновый поток для утренней рассылки |
| `handle_*` функции | Обработчики команд и кнопок |

## Ключевые декораторы

```python
@bot.message_handler(commands=['start'])  # Обработчик команды /start
@bot.message_handler(func=lambda m: m.text == "текст")  # По тексту
@bot.callback_query_handler(func=...)  # По нажатию на встроенную кнопку
```

---

## ИТОГ

Это **Telegram бот для школьного расписания**, который:
1. ✅ Хранит расписание в PostgreSQL
2. ✅ Позволяет ученикам смотреть своё расписание
3. ✅ Отправляет напоминания за 10 минут до урока
4. ✅ Отправляет утреннюю рассылку в 6:30
5. ✅ Работает на pyTelegramBotAPI (простой и понятный API)
6. ✅ Использует Django ORM для работы с БД
7. ✅ Запускает фоновые потоки для автоматизации

**Архитектура:**
- Основной поток: обрабатывает команды пользователей
- Поток 1: отправляет напоминания (каждые 30 сек проверяет время)
- Поток 2: отправляет рассылку (каждую минуту проверяет, 6:30?)
- БД: хранит учеников, расписание и настройки

Надеюсь, эта документация помогла вам разобраться! 🚀
