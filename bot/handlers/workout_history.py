from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import csv

router = Router()


@router.message(Command("workoutHistory"))
async def workout_history(message: Message):
    user_id = message.from_user.id
    history = get_workout_history(user_id)  # Функция для получения истории из файла

    if not history:
        await message.answer("У вас нет выполненных тренировок.")
    else:
        history_message = "\n".join(history)
        await message.answer(f"Ваша история тренировок:\n{history_message}")


def get_workout_history(user_id: int):
    # Чтение истории тренировок из файла
    history = []
    with open("data/workout_progress.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == str(user_id):
                history.append(f"{row[1]} в {row[2]}")
    return history
