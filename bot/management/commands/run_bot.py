from django.core.management.base import BaseCommand
import os
import sys

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

class Command(BaseCommand):
    help = 'Запуск Telegram бота'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Запуск Telegram бота...'))
        try:
            # Импортируем функцию main из telegram_bot.py
            from bot.telegram_bot import main
            main()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))
