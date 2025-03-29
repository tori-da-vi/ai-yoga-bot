import aiohttp
import aiohttp
import logging
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat

# Инициализируем логирование
logging.basicConfig(level=logging.INFO)

GIGACHAT_API_URL = ""
GIGACHAT_API_KEY = ""

# Инициализация модели GigaChat
llm = GigaChat(
    credentials=GIGACHAT_API_KEY,
    scope="GIGACHAT_API_PERS",
    model="GigaChat",
    verify_ssl_certs=False,  # Отключаем SSL сертификаты
    streaming=False,
)

# Создаем роутер
router = Router()

# Сохраняем историю сообщений в списке
messages = [
    SystemMessage(content="Ты профессиональный йог-наставник, который консультирует своих учеников только в сфере йоги.")
]

# Обработчик команды /coach
@router.message(Command("coach"))
async def coach(message: Message):
    user_name = message.from_user.full_name
    await message.answer(
        f"Здравствуй, {user_name}! Меня зовут Пабло, я твой гуру йог! Готов ответить на все интересующие тебя вопросы!")
    await message.answer("Напиши мне свой вопрос:")

    # Обновляем меню, чтобы была только кнопка "Завершить диалог с Пабло"
    button = KeyboardButton(text="Завершить диалог с Пабло")
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button]],  # Передаем список кнопок в keyboard
        resize_keyboard=True  # Автоматическое изменение размера клавиатуры
    )
    await message.answer("Для завершения диалога нажмите кнопку ниже.", reply_markup=keyboard)


# Обработчик кнопки "Завершить диалог с Пабло"
@router.message(lambda message: message.text == "Завершить диалог с Пабло")
async def end_dialog(message: Message):
    # Отправляем сообщение о завершении диалога
    await message.answer("Вы завершили диалог с Пабло. Возвращаемся в главное меню.")

    # Восстанавливаем стандартное меню
    button1 = KeyboardButton(text="📆 Расписание")  # Кнопка для расписания
    button2 = KeyboardButton(text="🧘🏻 Тренировка")  # Кнопка для тренировки
    button3 = KeyboardButton(text="⏰ История тренировок")  # Кнопка для истории тренировок
    button4 = KeyboardButton(text="👩‍💻 Обратная связь")  # Кнопка для обратной связи
    button5 = KeyboardButton(text="🪬 Коуч")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button1, button2],  # Строка с кнопками
            [button3, button4],  # Строка с кнопками
            [button5]  # Строка с кнопками
        ],
        resize_keyboard=True  # Автоматическое изменение размера клавиатуры
    )
    await message.answer("Выберите команду:", reply_markup=keyboard)



# Обработчик сообщений для чата с ИИ
@router.message()
async def handle_message(message: Message):
    user_input = message.text

    # Добавляем сообщение пользователя в историю
    messages.append(HumanMessage(content=user_input))

    # Получаем ответ от GigaChat
    try:
        res = llm.invoke(messages)
        # Добавляем ответ ИИ в историю
        messages.append(res)
        # Отправляем ответ пользователю
        await message.answer(res.content)
    except Exception as e:
        logging.error(f"Ошибка при получении ответа от GigaChat: {str(e)}")
        await message.answer("Произошла ошибка при получении ответа. Пожалуйста, попробуйте снова.")