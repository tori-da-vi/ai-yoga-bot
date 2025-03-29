from aiogram.fsm.state import State, StatesGroup

class RegistrationState(StatesGroup):
    name = State()
    experience = State()
    level = State()
