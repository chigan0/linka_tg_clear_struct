from aiogram.fsm.state import State, StatesGroup

class AdminState(StatesGroup):
	base_menu = State()
	new_user_id = State()
