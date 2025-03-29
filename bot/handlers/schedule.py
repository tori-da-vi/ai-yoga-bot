import asyncio
import csv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from aiogram import Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import datetime
import re

router = Router()


# Стейты для FSM
class ScheduleStates(StatesGroup):
    waiting_for_day_selection = State()
    waiting_for_additional_day = State()
    waiting_for_time_selection = State()
    finished_schedule = State()


# Список дней недели
days_of_week = ["Понеделник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

# Инициализация планировщика
scheduler = AsyncIOScheduler()


# Функции для работы с CSV

# Сохранение расписания в CSV
def save_schedule_to_csv(user_id, selected_days_with_time):
    # Проверяем, если расписание заполнено
    if selected_days_with_time:
        with open('schedule.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Для каждого дня и времени в расписании сохраняем строку
            for day, time in selected_days_with_time.items():
                writer.writerow([user_id, day, time])



# Удаление расписания из CSV
def delete_schedule_from_csv(user_id):
    rows = []
    with open("schedule.csv", mode="r") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] != str(user_id):
                rows.append(row)

    with open("schedule.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def update_schedule_in_csv(user_id, selected_days_with_time):
    # Считываем существующие данные из файла
    updated_rows = []
    with open('schedule.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            # Если для данного пользователя найден день, обновляем время
            if row[0] == str(user_id):
                day = row[1]
                if day in selected_days_with_time:
                    # Заменяем "Не задано" на введенное время
                    updated_rows.append([row[0], row[1], selected_days_with_time.get(day, "Не задано")])
                else:
                    updated_rows.append(row)
            else:
                updated_rows.append(row)

    # Перезаписываем файл с обновленными данными
    with open('schedule.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)



# Чтение расписания из CSV
def get_schedule_from_csv(user_id):
    schedule_info = {}

    try:
        with open('schedule.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            # Проходим по строкам файла
            for row in reader:
                if row[0] == str(user_id):  # Если это запись для данного пользователя
                    day = row[1]
                    time = row[2]
                    schedule_info[day] = time
    except FileNotFoundError:
        return None

    return schedule_info


# Обработка команды /schedule
@router.message(Command("schedule"))
async def schedule(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Установить расписание", callback_data="set_schedule"),
        InlineKeyboardButton(text="Сбросить расписание", callback_data="reset_schedule"),
        InlineKeyboardButton(text="Просмотреть расписание", callback_data="view_schedule")
    )
    await message.answer("Выберите действие:", reply_markup=builder.as_markup())


# Просмотр расписания
# Просмотр расписания
@router.callback_query(lambda c: c.data == "view_schedule")
async def view_schedule(callback_query: types.CallbackQuery, state: FSMContext):
    # Получаем данные из CSV
    schedule_info = get_schedule_from_csv(callback_query.from_user.id)

    if schedule_info:
        schedule_text = "Ваше расписание:\n"
        for day, time in schedule_info.items():
            if time != "Не задано":
                schedule_text += f"{day}: {time}\n"
            else:
                schedule_text += f"{day}: Не задано\n"
        await callback_query.message.edit_text(schedule_text)
    else:
        await callback_query.message.edit_text("Вы еще не установили расписание.")




# Сброс расписания
@router.callback_query(lambda c: c.data == "reset_schedule")
async def reset_schedule(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    delete_schedule_from_csv(callback_query.from_user.id)
    await callback_query.message.edit_text(
        "Ваше расписание было сброшено. Вы можете установить новое расписание."
    )


# Сброс расписания и установка нового
@router.callback_query(lambda c: c.data == "set_schedule")
async def set_schedule(callback_query: types.CallbackQuery, state: FSMContext):
    # Сначала сбрасываем старое расписание
    delete_schedule_from_csv(callback_query.from_user.id)

    # Устанавливаем новое расписание
    await state.set_state(ScheduleStates.waiting_for_day_selection)

    builder = InlineKeyboardBuilder()
    for day in days_of_week:
        builder.add(InlineKeyboardButton(text=day, callback_data=f"select_day_{day}"))

    await callback_query.message.edit_text("Выберите, в какие дни вы хотите заниматься:",
                                           reply_markup=builder.as_markup())




# Выбор дня
@router.callback_query(lambda c: c.data.startswith("select_day_"))
async def select_day(callback_query: types.CallbackQuery, state: FSMContext):
    selected_day = callback_query.data.split("select_day_")[1]
    data = await state.get_data()

    if "selected_days" not in data or not isinstance(data["selected_days"], list):
        data["selected_days"] = []

    data["selected_days"].append(selected_day)
    await state.update_data(data)

    remaining_days = [day for day in days_of_week if day not in data["selected_days"]]

    if remaining_days:
        builder = InlineKeyboardBuilder()
        for day in remaining_days:
            builder.add(InlineKeyboardButton(text=day, callback_data=f"select_day_{day}"))

        builder.add(InlineKeyboardButton(text="Готово", callback_data="finish_schedule"))
        await callback_query.message.edit_text(
            f"Вы выбрали: {', '.join(data['selected_days'])}. Выберите еще день или завершите.",
            reply_markup=builder.as_markup()
        )
        await state.set_state(ScheduleStates.waiting_for_additional_day)
    else:
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="Готово", callback_data="finish_schedule"))
        await callback_query.message.edit_text(
            f"Вот по каким дням вы выбрали заниматься: {', '.join(data['selected_days'])}. Теперь выберите время для каждого дня.",
            reply_markup=builder.as_markup()
        )
        await state.set_state(ScheduleStates.waiting_for_time_selection)


# Завершение установки расписания
# Завершение установки расписания
@router.callback_query(lambda c: c.data == "finish_schedule")
async def finish_schedule(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    days = data.get("selected_days", [])
    selected_days_with_time = data.get("selected_days_with_time", {})

    for day in days:
        if day not in selected_days_with_time:
            selected_days_with_time[day] = "Не задано"

    # Обновляем данные для сохранения в CSV
    await state.update_data(selected_days_with_time=selected_days_with_time)

    # Сохраняем в CSV только после того, как пользователь завершит ввод времени
    save_schedule_to_csv(callback_query.from_user.id, selected_days_with_time)

    await callback_query.message.answer(
        f"Вы выбрали следующие дни для занятий: {', '.join(days)}.\nТеперь укажите время для каждого дня."
    )

    await request_time_for_next_day(callback_query.message, state)

async def request_time_for_next_day(message: Message, state: FSMContext):
    data = await state.get_data()
    current_day_index = data.get("current_day_index", 0)
    days = data.get("selected_days", [])

    if current_day_index < len(days):
        day = days[current_day_index]
        await message.answer(f"Укажите время для дня {day} в формате ЧЧ:ММ:")
        await state.update_data({"selected_day": day})
    else:
        await message.answer("Все время для дней установлено! Уведомления будут отправляться в выбранное время.")
        await state.clear()

        # Запуск уведомлений
        for day, time in data["selected_days_with_time"].items():
            if time != "Не задано":
                hour, minute = map(int, time.split(":"))
                scheduler.add_job(send_notification, IntervalTrigger(hour=hour, minute=minute, day_of_week=day), args=[message.chat.id, day])



# Обработка ввода времени
# Обработка ввода времени
# Обработка ввода времени и его сохранение в CSV
@router.message(lambda message: re.match(r'^\d{2}:\d{2}$', message.text))
async def set_time(message: Message, state: FSMContext):
    data = await state.get_data()
    selected_day = data.get("selected_day")
    time = message.text.strip()

    try:
        # Разбираем введенное время
        hour, minute = map(int, time.split(":"))
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            raise ValueError("Неверное время")

        # Обновляем время для текущего дня в данных
        if "selected_days_with_time" not in data:
            data["selected_days_with_time"] = {}

        # Обновляем время для текущего дня
        data["selected_days_with_time"][selected_day] = time
        await state.update_data(data)

        # Обновляем файл CSV с новым временем
        update_schedule_in_csv(message.from_user.id, data["selected_days_with_time"])

        await message.answer(f"Время для дня {selected_day} установлено на {time}.")

        # Переходим к следующему дню или завершаем
        current_day_index = data.get("current_day_index", 0)
        days = data.get("selected_days", [])
        if current_day_index + 1 < len(days):
            await state.update_data({"current_day_index": current_day_index + 1})
            await request_time_for_next_day(message, state)
        else:
            await message.answer("Все время для дней установлено! Уведомления будут отправляться в выбранное время.")
            await state.clear()

    except ValueError:
        await message.answer("Время должно быть в формате ЧЧ:ММ и быть в пределах от 00:00 до 23:59.")


# Запуск планировщика
async def start_scheduler():
    scheduler.start()


if __name__ == "__main__":
    asyncio.run(start_scheduler())
