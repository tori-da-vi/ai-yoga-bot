from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from bot.states.registration_state import RegistrationState
from bot.utils.file_manager import save_to_csv
from aiogram.filters import Command
from datetime import datetime

router = Router()


# Старт регистрации
@router.message(Command("start"))
async def start_registration(message: Message, state: FSMContext):
    state_data = await state.get_data()
    if state_data.get("registered"):
        await message.answer("Вы уже зарегистрированы! Используйте /menu для просмотра доступных команд.")
        return

    await message.answer(
        "Привет! Данный бот поможет вам в тренировках йоги. Для начала давайте зарегистрируемся. Как вас зовут?")
    await state.set_state(RegistrationState.name)


# Получение имени пользователя
@router.message(RegistrationState.name)
async def ask_experience(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    # Запрос опыта с инлайн кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Новичок", callback_data="новичок")],
        [InlineKeyboardButton(text="Средний", callback_data="средний")],
        [InlineKeyboardButton(text="Продвинутый", callback_data="продвинутый")]
    ])
    await message.answer("Спасибо! Теперь выберите ваш уровень опыта йоги:", reply_markup=keyboard)
    await state.set_state(RegistrationState.experience)


# Обработка выбора уровня опыта через инлайн кнопки
@router.callback_query(RegistrationState.experience)
async def handle_experience(callback_query: CallbackQuery, state: FSMContext):
    experience = callback_query.data
    await state.update_data(experience=experience)
    # Подтверждаем выбор опыта
    await callback_query.answer(f"Вы выбрали уровень опыта: {experience}")
    await callback_query.message.answer("Теперь выберите ваш предпочтительный уровень тренировки:")

    # Кнопки для выбора уровня тренировки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Новичок", callback_data="новичок")],
        [InlineKeyboardButton(text="Средний", callback_data="средний")],
        [InlineKeyboardButton(text="Продвинутый", callback_data="продвинутый")]
    ])
    await callback_query.message.answer("Выберите уровень тренировки:", reply_markup=keyboard)
    await state.set_state(RegistrationState.level)


# Обработка выбора уровня тренировки через инлайн кнопки
@router.callback_query(RegistrationState.level)
async def handle_level(callback_query: CallbackQuery, state: FSMContext):
    level = callback_query.data.split("_")[0]  # Получаем только первую часть строки (новичок, средний или продвинутый)
    await state.update_data(level=level)
    await callback_query.answer(f"Вы выбрали уровень тренировки: {level}")

    # Сохраняем данные
    data = await state.get_data()
    name = data.get("name")
    experience = data.get("experience")
    level = data.get("level")
    user_id = callback_query.from_user.id
    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_to_csv(user_id, name, experience, level, registration_date)

    await callback_query.message.answer(
        f"Регистрация завершена, {name}! Теперь вы можете начать тренировки. Используйте /menu для просмотра доступных команд.")
    await state.clear()
