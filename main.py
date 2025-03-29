import asyncio
import logging
import csv
import random
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from bot.handlers import registration, schedule, workout, workout_history, feedback
from bot.middleware.registration_middleware import RegistrationMiddleware
from bot.handlers.menu import router as menu_router
from bot.handlers.coach import router as coach_router
from datetime import datetime
import pytz

# Настроим логирование
logging.basicConfig(level=logging.INFO)

API_TOKEN = ""

# Функция для отправки напоминания с цитатой
async def send_reminder(bot, user_ids):
    # Чтение цитат из файла
    quotes = read_yoga_quotes('yoga_quotes.txt')
    if quotes:
        # Выбираем случайную цитату
        quote = random.choice(quotes)
        for user_id in user_ids:
            try:
                await bot.send_message(user_id, quote)
                logging.info(f"Напоминание отправлено пользователю {user_id}: {quote}")
            except Exception as e:
                logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
    else:
        logging.error("Цитаты не найдены или файл пуст.")

# Чтение цитат из файла
def read_yoga_quotes(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            quotes = file.readlines()
        # Убираем лишние пробелы и символы новой строки
        return [quote.strip() for quote in quotes]
    except FileNotFoundError:
        logging.error(f"Файл {file_path} не найден.")
    except Exception as e:
        logging.error(f"Ошибка при чтении файла {file_path}: {e}")
    return []

# Чтение ID пользователей из файла users.csv
def get_registered_user_ids(file_path):
    user_ids = []
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user_ids.append(int(row['user_id']))  # Преобразуем user_id в целое число
    except FileNotFoundError:
        logging.error(f"Файл {file_path} не найден.")
    except Exception as e:
        logging.error(f"Ошибка при чтении файла {file_path}: {e}")
    return user_ids

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(RegistrationMiddleware())  # Подключаем middleware для проверки регистрации

    # Регистрируем роутеры
    dp.include_router(registration.router)
    dp.include_router(schedule.router)
    dp.include_router(workout.router)
    dp.include_router(workout_history.router)
    dp.include_router(feedback.router)
    dp.include_router(menu_router)
    dp.include_router(coach_router)

    logging.info("Бот запущен и слушает команды.")

    # Настроим планировщик задач
    scheduler = AsyncIOScheduler(timezone=pytz.timezone('Europe/Moscow'))

    # Читаем ID зарегистрированных пользователей из users.csv
    registered_user_ids = get_registered_user_ids('./data/users.csv')

    scheduler.add_job(
        send_reminder,
        CronTrigger(hour=13, minute=00),
        args=[bot, registered_user_ids],
        id="yoga_reminder",
        replace_existing=True
    )

    # Запуск планировщика
    scheduler.start()

    # Начнем polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
