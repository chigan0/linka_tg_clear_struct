from io import BytesIO
from datetime import datetime
from typing import List, Any, Optional
from pathlib import PosixPath

from aiogram import Router, Bot, types, F
from aiogram.types import user, Message, CallbackQuery, FSInputFile, ContentType as CT
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.exceptions import TelegramForbiddenError

from ..utils import base_func, send_answer, inline_keyboard, funcs_middlewares, generate_random_string, save_file, is_int
from ..settings import settings
from ..states import AdminState
from ..middlewares import SomeMiddleware

router = Router()


@router.callback_query(StateFilter(AdminState.base_menu))
async def report_info_btn(callback: CallbackQuery, bot: Bot, state: FSMContext, lang: dict):
	callbacks = {
		'add_user': add_new_user,
		'del_user': del_user
	}

	func = callbacks.get(callback.data)

	if func is not None:
		await func(callback.message, bot, state, lang)

