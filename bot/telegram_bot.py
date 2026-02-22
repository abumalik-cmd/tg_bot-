import telebot
from datetime import datetime, timedelta
import time
from threading import Thread
import pytz
"""Строка 1: import telebot
Что это: Подключает библиотеку для работы с Telegram Bot API.
Зачем: Именно эта библиотека позволяет:
Создавать бота (telebot.TeleBot(TOKEN))
Отвечать на сообщения
Отправлять клавиатуры
Реагировать на команды
Строка 2: from datetime import datetime, timedelta
Что это: Модуль для работы с датами и временем.
Зачем:
datetime — получать текущее время, сравнивать даты
timedelta — прибавлять/вычитать время (например, "за 10 минут до урока")
Строка 3: import time
Что это: Модуль для работы со временем (паузы, задержки).
Зачем: Нужен для циклов проверки расписания (например, проверять каждую минуту, не пора ли напоминать)
Строка 4: from threading import Thread
Что это: Модуль для создания параллельных потоков.
Зачем: Бот должен делать две вещи одновременно:
Поток 1: отвечать на сообщения пользователей
Поток 2: проверять время и отправлять напоминания об урока
Строка 5: import pytz
Что это: Библиотека для работы с часовыми поясами.
Зачем: Чтобы знать точное время в Москве, даже если сервер находится в другом часовом поясе."""

from bot.models import Student, GlobalLesson, PersonalLesson, AdminSettings

TOKEN = '8540461229:AAEY64b5fB0DkOoP96yS6DE9b4MHHmf0JIQ'
bot = telebot.TeleBot(TOKEN)

temp_data = {}
"""  Что это?
Пустой словарь для временных данных.

python
temp_data = {}
Зачем он нужен?
Представь диалог с ботом:

text
Бот: Введи свой класс
Пользователь: 10
Бот: Выбери букву
Пользователь: Б
Бот: Готово!
Проблема: Пока пользователь выбирает букву, бот должен запомнить, что класс уже 10. Но в базе данных сохранять рано — вдруг пользователь передумает?

Вот тут и нужен temp_data!"""
MSK_TZ = pytz.timezone('Europe/Moscow')

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


def get_lesson_time(lesson_number):
    lesson = LESSON_TIMES.get(lesson_number)
    if lesson:
        return lesson["start"], lesson["end"]
    return "??:??", "??:??"


def get_current_lesson_time():
    return datetime.now(MSK_TZ)


def normalize_letter(letter):
    if not letter:
        return None
    letter = letter.upper().strip()
    return letter if letter in ['А', 'Б', 'В', 'Г'] else None


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


def get_settings_keyboard(student):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = telebot.types.KeyboardButton("🔄 Сменить класс")
    btn2 = telebot.types.KeyboardButton("📋 Тип расписания")
    btn3 = telebot.types.KeyboardButton("🔙 Назад в меню")
    markup.add(btn1, btn2, btn3)
    return markup


def get_back_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("🔙 Назад в меню"))
    return markup


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


@bot.message_handler(func=lambda message: message.text == "🔙 Назад в меню")
def back_to_menu(message):
    user_id = message.chat.id
    try:
        student = Student.objects.get(telegram_id=user_id)
        show_main_menu(message, student)
    except Student.DoesNotExist:
        start(message)


@bot.message_handler(func=lambda message: message.text == "📅 Сегодня")
def handle_today(message):
    user_id = message.chat.id
    student = Student.objects.get(telegram_id=user_id)
    
    today_num = get_current_lesson_time().isoweekday()
    
    if today_num > 5:
        bot.send_message(
            message.chat.id,
            "🎉 *Сегодня выходной!* 🎉\n\n"
            "Отдыхай, набирайся сил и готовься к новой учебной неделе! 💪",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        return
    
    lessons, lesson_type = get_student_lessons(student, today_num)
    
    if not lessons:
        admin_settings = AdminSettings.objects.first()
        admin_contact = admin_settings.contact if admin_settings else "@Abumalik08"
        
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(
            "📝 Создать своё расписание", 
            callback_data="add_personal"
        ))
        markup.add(telebot.types.InlineKeyboardButton(
            f"✉️ Написать {admin_contact}", 
            url=f"https://t.me/{admin_contact.replace('@', '')}"
        ))
        
        bot.send_message(
            message.chat.id,
            f"📭 *Расписание не найдено*\n\n"
            f"Для класса *{student.grade}{student.letter}* пока нет глобального расписания в системе.\n\n"
            f"🔹 *Что можно сделать?*\n\n"
            f"1️⃣ Попросить господина {admin_contact} добавить расписание для вашего класса\n"
            f"   _(нажми кнопку ниже, чтобы написать ему)_\n\n"
            f"2️⃣ Создать своё личное расписание прямо в боте\n"
            f"   _(это займёт всего минуту!)_",
            parse_mode='Markdown',
            reply_markup=markup
        )
        return
    
    days = {1: "ПОНЕДЕЛЬНИК", 2: "ВТОРНИК", 3: "СРЕДА", 4: "ЧЕТВЕРГ", 5: "ПЯТНИЦА"}
    source = "🌍 Глобальное" if lesson_type == 'global' else "👤 Личное"
    
    text = f"📅 *{days[today_num]}*\n"
    text += f"📋 {source} расписание\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    now = get_current_lesson_time().strftime("%H:%M")
    
    for lesson in lessons:
        start, end = get_lesson_time(lesson.number)
        
        if start > now:
            status = " ⏳"
        elif end < now:
            status = " ✅"
        else:
            status = " 🔴"
        
        text += f"*{lesson.number}. {lesson.subject}*{status}\n"
        text += f"   ⏰ {start} - {end}\n\n"
    
    bot.send_message(
        message.chat.id, 
        text, 
        parse_mode='Markdown', 
        reply_markup=get_main_keyboard()
    )


@bot.message_handler(func=lambda message: message.text == "📆 Завтра")
def handle_tomorrow(message):
    user_id = message.chat.id
    student = Student.objects.get(telegram_id=user_id)
    
    tomorrow_num = get_current_lesson_time().isoweekday() + 1
    
    if tomorrow_num == 6:
        bot.send_message(
            message.chat.id,
            "🎉 *Завтра суббота - выходной!* 🎉\n\n"
            "Планируй свои выходные и отдыхай! 🌟",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        return
    
    if tomorrow_num == 7:
        tomorrow_num = 1
    
    lessons, lesson_type = get_student_lessons(student, tomorrow_num)
    
    if not lessons:
        bot.send_message(
            message.chat.id,
            "📭 *На завтра расписание отсутствует*",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        return
    
    days = {1: "ПОНЕДЕЛЬНИК", 2: "ВТОРНИК", 3: "СРЕДА", 4: "ЧЕТВЕРГ", 5: "ПЯТНИЦА"}
    source = "🌍 Глобальное" if lesson_type == 'global' else "👤 Личное"
    
    text = f"📆 *{days[tomorrow_num]} (завтра)*\n"
    text += f"📋 {source} расписание\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for lesson in lessons:
        start, end = get_lesson_time(lesson.number)
        text += f"*{lesson.number}. {lesson.subject}*\n"
        text += f"   ⏰ {start} - {end}\n\n"
    
    bot.send_message(
        message.chat.id, 
        text, 
        parse_mode='Markdown', 
        reply_markup=get_main_keyboard()
    )


@bot.message_handler(func=lambda message: message.text == "📚 Неделя")
def handle_week(message):
    user_id = message.chat.id
    student = Student.objects.get(telegram_id=user_id)
    
    days = {1: "ПН", 2: "ВТ", 3: "СР", 4: "ЧТ", 5: "ПТ"}
    source = "🌍 Глобальное" if student.use_global else "👤 Личное"
    
    text = f"📚 *Расписание на неделю*\n"
    text += f"📋 {source} расписание\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n"
    
    for day_num in range(1, 6):
        lessons, _ = get_student_lessons(student, day_num)
        text += f"\n*{days[day_num]}:*\n"
        
        if lessons:
            subjects = []
            for lesson in lessons:
                start, _ = get_lesson_time(lesson.number)
                subjects.append(f"{lesson.number}.{lesson.subject} ({start})")
            text += " | ".join(subjects)
        else:
            text += "_нет уроков_"
        
        text += "\n"
    
    bot.send_message(
        message.chat.id, 
        text, 
        parse_mode='Markdown', 
        reply_markup=get_main_keyboard()
    )


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
    
    bot.send_message(
        message.chat.id, 
        text, 
        parse_mode='Markdown', 
        reply_markup=get_main_keyboard()
    )


@bot.message_handler(func=lambda message: message.text == "⚙️ Настройки")
def handle_settings(message):
    user_id = message.chat.id
    student = Student.objects.get(telegram_id=user_id)
    
    text = (
        f"⚙️ *НАСТРОЙКИ*\n\n"
        f"👤 *Имя:* {student.name}\n"
        f"🎓 *Класс:* {student.grade}{student.letter}\n"
        f"📋 *Тип:* {'🌍 Глобальное' if student.use_global else '👤 Личное'}\n\n"
        f"*Выбери действие:*"
    )
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode='Markdown',
        reply_markup=get_settings_keyboard(student)
    )


@bot.message_handler(func=lambda message: message.text == "🔄 Сменить класс")
def change_class(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=4)
    for g in range(1, 12):
        markup.add(telebot.types.InlineKeyboardButton(
            str(g), 
            callback_data=f"grade_{g}"
        ))
    
    bot.send_message(
        message.chat.id,
        "🔄 *Смена класса*\n\n"
        "📚 Выбери свой новый класс:",
        parse_mode='Markdown',
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == "📋 Тип расписания")
def change_schedule_type(message):
    user_id = message.chat.id
    student = Student.objects.get(telegram_id=user_id)
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    
    global_text = "✅ Глобальное" if student.use_global else "🌍 Глобальное"
    personal_text = "✅ Личное" if not student.use_global else "👤 Личное"
    
    markup.add(
        telebot.types.InlineKeyboardButton(global_text, callback_data="use_global"),
        telebot.types.InlineKeyboardButton(personal_text, callback_data="use_personal"),
        telebot.types.InlineKeyboardButton("📝 Создать личное", callback_data="add_personal")
    )
    
    bot.send_message(
        message.chat.id,
        f"📋 *Тип расписания*\n\n"
        f"🌍 *Глобальное* - общее для всего класса\n"
        f"👤 *Личное* - твоё индивидуальное\n\n"
        f"Выбери нужный:",
        parse_mode='Markdown',
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == "ℹ️ Информация")
def handle_info(message):
    """Показывает меню с информацией о боте"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        telebot.types.InlineKeyboardButton("📖 О боте", callback_data="about_simple"),
        telebot.types.InlineKeyboardButton("🔧 Техническая информация", callback_data="about_tech")
    )
    
    bot.send_message(
        message.chat.id,
        "ℹ️ *Информация*\n\n"
        "Выбери, что хочешь узнать:",
        parse_mode='Markdown',
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.message.chat.id
    student = Student.objects.get(telegram_id=user_id)
    
    if call.data.startswith('grade_'):
        grade = int(call.data.split('_')[1])
        temp_data[user_id] = {'grade': grade}
        
        markup = telebot.types.InlineKeyboardMarkup(row_width=4)
        for letter in ['А', 'Б', 'В', 'Г']:
            markup.add(telebot.types.InlineKeyboardButton(
                letter, 
                callback_data=f"letter_{letter}"
            ))
        
        bot.edit_message_text(
            f"📚 *Класс {grade}*\n\n"
            f"Теперь выбери букву:",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
    
    elif call.data.startswith('letter_'):
        letter = call.data.split('_')[1]
        grade = temp_data[user_id]['grade']
        
        student.grade = grade
        student.letter = letter
        student.save()
        
        bot.edit_message_text(
            f"✅ *Класс успешно установлен!*\n\n"
            f"📚 Твой класс: *{grade}{letter}*",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        
        show_main_menu(call.message, student)
        del temp_data[user_id]
    
    elif call.data == 'use_global':
        student.use_global = True
        student.save()
        
        bot.answer_callback_query(call.id, "✅ Включено глобальное расписание")
        bot.edit_message_text(
            "✅ *Глобальное расписание активировано!*\n\n"
            "🌍 Теперь ты видишь общее расписание для всего класса.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        time.sleep(2)
        show_main_menu(call.message, student)
    
    elif call.data == 'use_personal':
        student.use_global = False
        student.save()
        
        bot.answer_callback_query(call.id, "✅ Включено личное расписание")
        bot.edit_message_text(
            "✅ *Личное расписание активировано!*\n\n"
            "👤 Теперь ты видишь только своё расписание.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        time.sleep(2)
        show_main_menu(call.message, student)
    
    elif call.data == 'add_personal':
        temp_data[user_id] = {'action': 'add_personal', 'step': 'day'}
        bot.edit_message_text(
            "📝 *Создание личного расписания*\n\n"
            "Введи день недели (цифру):\n\n"
            "1️⃣ - Понедельник\n"
            "2️⃣ - Вторник\n"
            "3️⃣ - Среда\n"
            "4️⃣ - Четверг\n"
            "5️⃣ - Пятница",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
    
    elif call.data == 'about_simple':
        text = (
            "🤖 *О БОТЕ РАСПИСАНИЯ*\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            
            "👨‍💻 *Разработчик:* @Abumalik08\n\n"
            
            "✨ *ЧТО УМЕЕТ БОТ:*\n\n"
            
            "📅 *Расписание*\n"
            "   • Сегодня\n"
            "   • Завтра\n"
            "   • Вся неделя\n\n"
            
            "⏰ *Напоминания*\n"
            "   • Утренняя рассылка в 6:30\n"
            "   • За 10 минут до урока\n\n"
            
            "📋 *Два типа*\n"
            "   • 🌍 Глобальное - для всего класса\n"
            "   • 👤 Личное - твоё расписание\n\n"
            
            "⚙️ *Настройки*\n"
            "   • Смена класса\n"
            "   • Переключение типа\n\n"
            
            "💡 *КАК ПОЛЬЗОВАТЬСЯ?*\n"
            "1. Выбери класс\n"
            "2. Смотри расписание\n"
            "3. Получай напоминания\n\n"
            
            "📞 *По вопросам:* @Abumalik08\n\n"
            
            "🌟 *Учись на отлично!* 📚"
        )
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
    
    elif call.data == 'about_tech':
        text = (
            "🔧 *ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ*\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            
            "📊 *АРХИТЕКТУРА БОТА:*\n\n"
            
            "🗄️ *База данных (PostgreSQL):*\n"
            "   • Student - данные учеников\n"
            "     (telegram_id, имя, класс, буква, тип расписания)\n"
            "   • GlobalLesson - глобальное расписание\n"
            "     (класс, буква, день, номер урока, предмет)\n"
            "   • PersonalLesson - личное расписание\n"
            "     (ученик, день, номер урока, предмет)\n"
            "   • AdminSettings - настройки администратора\n\n"
            
            "⚙️ *ЛОГИКА РАБОТЫ:*\n\n"
            
            "*get_student_lessons():*\n"
            "1. Если use_global=True:\n"
            "   → Ищет уроки в GlobalLesson для класса/буквы\n"
            "2. Если нет или use_global=False:\n"
            "   → Возвращает PersonalLesson\n\n"
            
            "*get_next_lesson():*\n"
            "1. Проверяет день недели (ПН-ПТ)\n"
            "2. Получает все уроки на сегодня\n"
            "3. Сравнивает текущее время со временем начала\n"
            "4. Возвращает первый непройденный урок\n\n"
            
            "🔔 *ФОНОВЫЕ ПРОЦЕССЫ:*\n\n"
            
            "*morning_sender():*\n"
            "• Работает в отдельном потоке\n"
            "• Каждую минуту проверяет время\n"
            "• В 6:30 отправляет расписание всем\n\n"
            
            "*reminder_checker():*\n"
            "• Работает в отдельном потоке\n"
            "• Каждые 30 сек проверяет уроки\n"
            "• За 10 минут до урока - напоминание\n"
            "• Алгоритм:\n"
            "  1. Для каждого ученика\n"
            "  2. Получить расписание на сегодня\n"
            "  3. Для каждого урока:\n"
            "     - Время напоминания = начало - 10 мин\n"
            "     - Если сейчас это время → отправить\n\n"
            
            "⏰ *ВРЕМЕННЫЕ ДАННЫЕ:*\n\n"
            "temp_data = {}\n"
            "• Хранит промежуточные данные пользователя\n"
            "• Используется при выборе класса\n"
            "• Используется при создании личного расписания\n"
            "• Автоматически очищается после завершения\n\n"
            
            "🔧 *ТЕХНОЛОГИИ:*\n"
            "• Python 3.x\n"
            "• pyTelegramBotAPI (telebot)\n"
            "• Django ORM\n"
            "• PostgreSQL\n"
            "• pytz (московское время)\n"
            "• Threading (фоновые задачи)\n\n"
            
            "🎯 *ПОДДЕРЖКА:*\n"
            "• Классы: 1-11 (А-Г)\n"
            "• Дни: ПН-ПТ\n"
            "• Уроки: 1-8\n"
            "• Часовой пояс: МСК"
        )
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )


@bot.message_handler(func=lambda message: message.chat.id in temp_data)
def handle_add_personal(message):
    user_id = message.chat.id
    data = temp_data[user_id]
    
    if data.get('action') != 'add_personal':
        return
    
    if data['step'] == 'day':
        try:
            day = int(message.text.strip())
            
            if day < 1 or day > 5:
                bot.reply_to(
                    message, 
                    "❌ День должен быть от 1 до 5",
                    parse_mode='Markdown'
                )
                return
            
            data['day'] = day
            data['step'] = 'subjects'
            
            days_names = {1: "Понедельник", 2: "Вторник", 3: "Среда", 4: "Четверг", 5: "Пятница"}
            
            bot.send_message(
                user_id,
                f"✅ День: *{days_names[day]}*\n\n"
                f"📝 Теперь введи предметы\n\n"
                f"*Каждый с новой строки!*\n\n"
                f"*Пример:*\n"
                f"Русский язык\n"
                f"Математика\n"
                f"Литература",
                parse_mode='Markdown',
                reply_markup=get_back_keyboard()
            )
        
        except ValueError:
            bot.reply_to(message, "❌ Нужно ввести число от 1 до 5")
    
    elif data['step'] == 'subjects':
        subjects = [s.strip() for s in message.text.split('\n') if s.strip()]
        
        if not subjects:
            bot.send_message(user_id, "❌ Нет предметов!")
            return
        
        student = Student.objects.get(telegram_id=user_id)
        day = data['day']
        
        PersonalLesson.objects.filter(student=student, day=day).delete()
        
        for i, subject in enumerate(subjects, start=1):
            PersonalLesson.objects.create(
                student=student,
                day=day,
                number=i,
                subject=subject
            )
        
        days_full = {1: "Понедельник", 2: "Вторник", 3: "Среда", 4: "Четверг", 5: "Пятница"}
        
        confirmation = f"✅ *Личное расписание создано!*\n\n"
        confirmation += f"📅 {days_full[day]}\n"
        confirmation += f"📚 Добавлено: {len(subjects)} уроков\n\n"
        
        for i, subject in enumerate(subjects, start=1):
            start_time, end_time = get_lesson_time(i)
            confirmation += f"{i}. {subject} ({start_time}-{end_time})\n"
        
        confirmation += "\n💡 Переключись на личное в настройках!"
        
        bot.send_message(
            user_id,
            confirmation,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        
        del temp_data[user_id]


def reminder_checker():
    print("🔔 Поток напоминаний запущен")
    
    while True:
        try:
            now = get_current_lesson_time()
            today_num = now.isoweekday()
            
            if today_num <= 5:
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


def morning_sender():
    print("📬 Поток рассылки запущен")
    
    while True:
        try:
            now = get_current_lesson_time()
            
            if now.hour == 6 and now.minute == 30:
                students = Student.objects.all()
                today_num = now.isoweekday()
                
                if today_num <= 5:
                    for student in students:
                        try:
                            lessons, lesson_type = get_student_lessons(student, today_num)
                            
                            if lessons:
                                days = {1: "ПОНЕДЕЛЬНИК", 2: "ВТОРНИК", 3: "СРЕДА", 4: "ЧЕТВЕРГ", 5: "ПЯТНИЦА"}
                                source = "🌍" if lesson_type == 'global' else "👤"
                                
                                text = f"{source} *Доброе утро, {student.name}!*\n\n"
                                text += f"📅 *{days[today_num]}*\n"
                                text += "━━━━━━━━━━━━━━━━━━━━\n\n"
                                
                                for lesson in lessons:
                                    start, end = get_lesson_time(lesson.number)
                                    text += f"*{lesson.number}. {lesson.subject}*\n"
                                    text += f"   ⏰ {start} - {end}\n\n"
                                
                                text += "💪 *Удачного дня!*"
                                
                                bot.send_message(student.telegram_id, text, parse_mode='Markdown')
                                print(f"✅ Рассылка: {student.name}")
                        
                        except Exception as e:
                            print(f"❌ Ошибка: {e}")
            
            time.sleep(60)
            
        except Exception as e:
            print(f"❌ Ошибка в morning_sender: {e}")
            time.sleep(60)


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


if __name__ == '__main__':
    main()
