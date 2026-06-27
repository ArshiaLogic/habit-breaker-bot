from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    waiting_for_post_text = State()
    waiting_for_broadcast = State()
