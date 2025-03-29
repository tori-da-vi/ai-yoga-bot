import logging
from aiogram import Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from bot.handlers import workout
from bot.handlers import feedback
from bot.handlers import schedule
from bot.handlers import workout_history
from bot.handlers import coach

# Настроим логирование
logging.basicConfig(level=logging.INFO)

router = Router()

# Обработчик команды /menu
@router.message(Command("menu"))
async def show_menu(message: Message):
    logging.info("Команда /menu активирована")  # Логирование для проверки

    # Создаём кнопки с новым текстом
    button1 = KeyboardButton(text="📆 Расписание")  # Кнопка для расписания
    button2 = KeyboardButton(text="🧘🏻 Тренировка")  # Кнопка для тренировки
    button3 = KeyboardButton(text="⏰ История тренировок")  # Кнопка для истории тренировок
    button4 = KeyboardButton(text="👩‍💻 Обратная связь")  # Кнопка для обратной связи
    button5 = KeyboardButton(text="🪬 Коуч")  # Кнопка для коуча

    # Создаём клавиатуру и добавляем кнопки
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button1, button2],  # Строка с кнопками
            [button3, button4],  # Строка с кнопками
            [button5]  # Строка с кнопками
        ],
        resize_keyboard=True  # Автоматическое изменение размера клавиатуры
    )

    # Отправляем сообщение с клавиатурой
    await message.answer("Доступные команды:", reply_markup=keyboard)

# Обработка нажатия кнопки "Расписание"
@router.message(lambda message: message.text == "📆 Расписание")
async def schedule_button(message: Message):
    # Вызов команды /schedule из файла schedule.py
    await schedule.schedule(message)

# Обработка нажатия кнопки "Тренировка"
@router.message(lambda message: message.text == "🧘🏻 Тренировка")
async def workout_button(message: Message):
    # Вызов команды /workout из файла workout.py
    await workout.workout(message)

# Обработка нажатия кнопки "История тренировок"
@router.message(lambda message: message.text == "⏰ История тренировок")
async def workout_history_button(message: Message):
    # Вызов команды /workoutHistory из файла workout_history.py
    await workout_history.workout_history(message)

# Обработка нажатия кнопки "Обратная связь"
@router.message(lambda message: message.text == "👩‍💻 Обратная связь")
async def feedback_button(message: Message, state: FSMContext):
    # Вызов команды /feedback из файла feedback.py
    await feedback.feedback(message, state)



# Обработка нажатия кнопки "Коуч"
@router.message(lambda message: message.text == "🪬 Коуч")
async def coach_button(message: Message):
    # Вызов команды /coach из файла coach.py
    await coach.coach(message)

