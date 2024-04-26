from typing import Union, Dict

from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def make_row_keyboard(items: dict) -> ReplyKeyboardMarkup:
	row = [KeyboardButton(text=item, request_location=items[item]) for item in items]
	return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


# Функция для создания inline кнопок
def inline_keyboard(items: Union[dict, list], 
		default = True, 
		top_block: Dict[str, str] = None,
		bottom_block: Dict[str, str] = None,
		single_buttons: bool = False,
		row = 1
	) -> InlineKeyboardMarkup:
	row_num: int = 0
	key_num: int = 0
	key_len: int = len(items.keys())
	buttons: list = []
	ram: list = []

	if top_block is not None:
		for i in top_block:
			buttons.append([InlineKeyboardButton(text=i, callback_data=top_block[i])])

	for it in items:
		text = it

		if default:
			button = InlineKeyboardButton(text=text, callback_data=items[it])

		else:
			button_type = items[it]['button_type']
			value = items[it]['value']
			button = InlineKeyboardButton(
					text=text,
					callback_data=value if button_type == 'c_data' else None,
					switch_inline_query=value if button_type == 's_inline_query' else None,
					switch_inline_query_current_chat=value if button_type == 's_inline_query_c' else None,
					url=value if button_type == 's_url' else None, 
				)
		
		if row > 1:
			ram.append(button)
			row_num += 1
			if row_num >= row or key_num+1 >= key_len:
				buttons.append(ram)
				ram = []
				row_num = 0
		
		else:
			buttons.append([button])

		key_num += 1

	if bottom_block is not None:
		for i in bottom_block:
			buttons.append([InlineKeyboardButton(text=i, callback_data=bottom_block[i])])

	return InlineKeyboardMarkup(row_width=2, inline_keyboard=buttons)