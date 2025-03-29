from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
import time
import csv
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.utils.user_data import get_user_experience
from aiogram.fsm.context import FSMContext
import os


router = Router()


@router.message(Command("workout"))
async def workout(message: Message):
    user_id = message.from_user.id
    experience = get_user_experience(user_id)  # Получаем опыт пользователя

    # Логика выбора тренировки в зависимости от опыта
    if experience == "новичок":
        workout_type = "Простая йога"
    elif experience == "средний":
        workout_type = "Средняя йога"
    else:
        workout_type = "Продвинутая йога"

    # Отправка информации о тренировке
    await message.answer(f"Вы выбрали тренировку: {workout_type}. Начинаем!")
    await send_workout_exercises(message, workout_type)  # Ваша функция для отправки упражнений


async def send_workout_exercises(message: Message, workout_type: str):
    # Пример упражнений без картинок
    exercises = {
        "Простая йога": [
            {
                "pose": "Сурья Намаскар",
                "description": (
                    "Сурья Намаскар (Приветствие Солнцу) — это комплекс из 12 поз, "
                    "которые помогают улучшить гибкость, силу и выносливость. Это упражнение "
                    "активирует все части тела и способствует улучшению циркуляции крови и дыхательной функции."
                ),
                "duration": 15  # Длительность упражнения в секундах
            },
            {
                "pose": "Поза дерева",
                "description": (
                    "Поза дерева (Врикшасана) — это поза стоя, которая помогает улучшить баланс, "
                    "укрепляет ноги и спину, а также развивает концентрацию и устойчивость. "
                    "Она символизирует корни и связь с природой."
                ),
                "duration": 15  # Длительность упражнения в секундах
            }
        ],
        "Средняя йога": [
            {
                "pose": "Поза воина",
                "description": (
                    "Поза воина (Вирабхадрасана) — это мощная поза, которая развивает силу и стойкость. "
                    "Она помогает укрепить ноги, раскрыть грудную клетку и улучшить гибкость бедер. "
                    "Также она стимулирует уверенность в себе и стойкость."
                ),
                "duration": 15  # Длительность упражнения в секундах
            },
            {
                "pose": "Поза собаки мордой вниз",
                "description": (
                    "Поза собаки мордой вниз (Адхо Мукха Шванасана) — это базовая поза йоги, "
                    "которая растягивает спину, улучшает гибкость и помогает снять напряжение в теле. "
                    "Она также улучшает кровообращение и способствует расслаблению."
                ),
                "duration": 15  # Длительность упражнения в секундах
            }
        ],
        "Продвинутая йога": [
            {
                "pose": "Поза лотоса",
                "description": (
                    "Поза лотоса (Падмасана) — это медитативная поза, которая помогает углубить практику медитации. "
                    "Она способствует спокойствию и внутреннему равновесию, а также улучшает циркуляцию в области таза. "
                    "Это поза для тех, кто хочет развить гибкость и стойкость."
                ),
                "duration": 15  # Длительность упражнения в секундах
            },
            {
                "pose": "Поза стойки на голове",
                "description": (
                    "Поза стойки на голове (Сарвангасана) — это одна из самых сложных поз, "
                    "которая развивает силу и баланс. Она помогает улучшить кровообращение, укрепляет плечи и спину. "
                    "Стоя на голове, вы активируете все тело и получаете чувство освобождения и свободы."
                ),
                "duration": 15  # Длительность упражнения в секундах
            }
        ]
    }

    # Перебор упражнений в выбранной тренировке
    for exercise in exercises[workout_type]:
        # Отправка упражнения с описанием
        exercise_message = await message.answer(f"{exercise['pose']}\n{exercise['description']}")

        # Запуск таймера на упражнение
        await start_timer(message, exercise_message, exercise['duration'])

    # Завершение тренировки
    await message.answer("Тренировка завершена!")
    await save_workout_progress(message.from_user.id)

    # Запросить отзыв
    await ask_feedback(message)


# Функция для создания кнопок
async def ask_feedback(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data="yes"),
                InlineKeyboardButton(text="Нет", callback_data="no")
            ]
        ]
    )

    await message.answer("Вам понравилась тренировка?", reply_markup=keyboard)

# Обработка нажатия кнопки "Да"
@router.callback_query(F.data == "yes")
async def handle_yes(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    experience = get_user_experience(user_id)
    # Ответ на нажатие кнопки "Да"
    await call.message.answer("Спасибо за отзыв! Мы рады, что вам понравилось!")
    await call.message.delete_reply_markup()  # Убираем клавиатуру

    # Завершаем текущий процесс, чтобы нельзя было повторно нажать
    await state.clear()
    await ask_new_level(call.message, experience)

# Обработка нажатия кнопки "Нет"
@router.callback_query(F.data == "no")
async def handle_no(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    experience = get_user_experience(user_id)
    # Ответ на нажатие кнопки "Нет"
    await call.message.answer("Спасибо за отзыв! Мы постараемся улучшиться!")
    await call.message.delete_reply_markup()  # Убираем клавиатуру

    # Завершаем текущий процесс, чтобы нельзя было повторно нажать
    await state.clear()
    await ask_new_level(call.message, experience)


# Функция для запроса уровня после тренировки
async def ask_new_level(message: Message, current_level: str):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="новичок", callback_data="novice"),
                InlineKeyboardButton(text="средний", callback_data="intermediate"),
                InlineKeyboardButton(text="продвинутый", callback_data="advanced"),
            ]
        ]
    )

    await message.answer(f"Ваш уровень - {current_level}. Как вы себя оцениваете сейчас?", reply_markup=keyboard)


# Обработка выбора нового уровня
@router.callback_query(F.data == "novice")
async def handle_novice(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    # Обновляем уровень в users.csv
    update_user_level(user_id, "новичок")
    await call.message.answer("Ваш уровень обновлен на 'Новичок'. Спасибо за отзыв!")
    await call.message.delete_reply_markup()  # Убираем клавиатуру
    await state.clear()


@router.callback_query(F.data == "intermediate")
async def handle_intermediate(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    # Обновляем уровень в users.csv
    update_user_level(user_id, "средний")
    await call.message.answer("Ваш уровень обновлен на 'Средний'. Спасибо за отзыв!")
    await call.message.delete_reply_markup()  # Убираем клавиатуру
    await state.clear()


@router.callback_query(F.data == "advanced")
async def handle_advanced(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    # Обновляем уровень в users.csv
    update_user_level(user_id, "продвинутый")
    await call.message.answer("Ваш уровень обновлен на 'Продвинутый'. Спасибо за отзыв!")
    await call.message.delete_reply_markup()  # Убираем клавиатуру
    await state.clear()


# Функция для обновления уровня в users.csv
def update_user_level(user_id: int, new_level: str):
    # Указываем путь к файлу с пользователями
    file_path = './data/users.csv'

    # Проверяем, существует ли директория, если нет — создаем
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    users = []
    # Читаем все данные из файла
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            users = list(reader)
    except FileNotFoundError:
        pass

    # Обновляем уровень
    user_found = False
    for user in users:
        if user[0].isdigit() and int(user[0]) == user_id:  # Проверяем, что user[0] это число
            user[3] = new_level  # Обновляем уровень
            user_found = True
            break

    if not user_found:
        # Если пользователя нет в файле, добавляем нового с уровнем и пустыми полями для имени и даты рождения
        users.append([str(user_id), '', '', new_level])

    # Записываем обновленные данные в файл
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(users)



async def start_timer(message: Message, exercise_message: Message, duration: int):
    # Таймер для тренировки
    for i in range(duration, 0, -1):
        time.sleep(1)
        # Обновление сообщения с оставшимся временем
        if i == 1:
            # Переход к следующей позе
            await exercise_message.edit_text(f"{exercise_message.text}\nПереходим к следующей позе.")
            break
        elif i % 5 == 0:  # Каждые 5 секунд обновляем
            await exercise_message.edit_text(
                f"{exercise_message.text}\n{str(i)} секунд осталось до следующего упражнения.")


async def save_workout_progress(user_id: int):
    # Сохраняем прогресс в файл
    with open("data/workout_progress.csv", "a", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, "Тренировка завершена", time.strftime("%Y-%m-%d %H:%M:%S")])



