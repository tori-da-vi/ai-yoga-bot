import csv
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


router = Router()

# Определяем состояния для FSM
class FeedbackState(StatesGroup):
    waiting_for_feedback = State()

# Обработчик команды /feedback
@router.message(Command("feedback"))
async def feedback(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, напишите ваш отзыв для тренера. Мы ценим ваше мнение!")
    await state.set_state(FeedbackState.waiting_for_feedback)  # Устанавливаем состояние ожидания отзыва

# Обработчик текста после команды /feedback
@router.message(F.text, FeedbackState.waiting_for_feedback)
async def receive_feedback(message: Message, state: FSMContext):
    # Сохраняем отзыв в CSV-файл
    with open("feedbacks.csv", mode="a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([message.from_user.id, message.from_user.full_name, message.text])

    # Ответ пользователю
    await message.answer("Спасибо за отзыв по работе бота!")

    # Сбрасываем состояние FSM, чтобы бот не реагировал на последующие сообщения
    await state.clear()
