from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_interests = State()
    waiting_for_level = State()

class Settings(StatesGroup):
    changing_level = State()
    changing_interests = State()

class LessonFlow(StatesGroup):
    viewing_lesson = State()
