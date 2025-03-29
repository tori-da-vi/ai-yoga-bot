from aiogram import BaseMiddleware
from aiogram.types import Message
import csv


class RegistrationMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        user_id = event.from_user.id
        with open("./data/users.csv", "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            # Фильтруем пустые строки и строки с недостающими данными
            valid_rows = [row for row in reader if row and len(row) > 0]

            # Проверяем, что user_id существует в первой колонке
            if str(user_id) in [row[0] for row in valid_rows]:
                if event.text.startswith("/start"):
                    await event.answer("Вы уже зарегистрированы! Используйте /menu для просмотра доступных команд.")
                    return
        return await handler(event, data)
