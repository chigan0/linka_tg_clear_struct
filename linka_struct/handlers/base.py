from typing import List, Any

from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram import Router, Bot, types, F
from aiogram.types import Message, chat, user, CallbackQuery, ChatMemberAdministrator, FSInputFile, ContentType as CT
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.exceptions import TelegramForbiddenError

from ..utils import base_func, send_answer, inline_keyboard, LangsSingleton
from ..settings import settings
from ..crud import add_new_group, get_group_by_caht_id

router = Router()

async def check_left_chat(message: Message, bot: Bot, state: FSMContext, lang: LangsSingleton):
	chat_data: chat.Chat = message.chat

	try:
		left_info = getattr(message, 'left_chat_participant')
		
		if left_info['id'] != settings.ME.id: return None

		async with settings.get_db(True) as session:
			group = await get_group_by_caht_id(session, chat_data.id)

			if group is not None:
				await session.delete(group)

	except AttributeError:
		return None


# Responds to start command
@router.message(Command(commands=['start']))
async def cmd_send_welcome(message: Message, bot: Bot, state: FSMContext, lang: LangsSingleton):
	await base_func(message, bot, state, lang, False)


async def add_to_chat(message: Message, bot: Bot, state: FSMContext, lang: LangsSingleton):
	try:
		member_info = getattr(message, 'new_chat_member')
		user_data: user.User = message.from_user
		chat_data: chat.Chat = message.chat

		if member_info['id'] != settings.ME.id:
			return None

		if not user_data.id in settings.SUPER_USERS:
			await message.answer(lang.get_msg_key('Your is not a admin').format(username=user_data.first_name), parse_mode='Markdown')
			await message.answer(lang.get_msg_key('Bot left a chat'), parse_mode='Markdown')
			return await bot.leave_chat(chat_data.id)

		chat_member_data: ChatMemberStatus = await bot.get_chat_member(chat_id=chat_data.id, user_id=settings.ME.id)

		if chat_member_data.status == ChatMemberStatus.RESTRICTED:
			return await bot.leave_chat(chat_data.id)

		async with settings.get_db(True) as session:
			add_new_group(session, str(chat_data.id), chat_data.title, chat_data.type)

		await message.answer(lang.get_msg_key('Bot added to group').format(bot_name=settings.ME.first_name), parse_mode='Markdown')

	except Exception as e:
		print(e)
		return None


@router.message(StateFilter(None))
async def all_message_callback(message: Message, bot: Bot, state: FSMContext, lang: LangsSingleton):
	await check_left_chat(message, bot, state, lang)
	await add_to_chat(message, bot, state, lang)


# All Quey Callback
@router.callback_query(StateFilter(None))
async def all_callback_query(callback: CallbackQuery, bot: Bot, state: FSMContext, lang: LangsSingleton):
	pass

