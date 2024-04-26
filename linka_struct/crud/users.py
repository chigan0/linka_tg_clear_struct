from datetime import datetime
from typing import Union, List, Optional, Any
from datetime import datetime

from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String, or_
from sqlalchemy.orm import Session
from aiogram.types import user

from ..models import User, ActiveGroups


# Create new User
def add_user(user_data: user.User, session: Session) -> User:
	user = User(user_tg_id=str(user_data.id), 
				first_name=user_data.first_name,
				last_name=user_data.last_name,
				username=user_data.username,
				# url=user_data.
				# language_code=user_data.language_code,
				date_created=datetime.now())
	
	session.add(user)
	return user


def add_new_group(session: Session, chat_id: Union[str, int], title: str, group_type: str) -> ActiveGroups:
	group = ActiveGroups(chat_id=str(chat_id), title=title, group_type=group_type)
	session.add(group)

	return group


async def get_group_by_caht_id(session: Session, chat_id: Union[str, int]) -> Optional[ActiveGroups]:
	q = await session.execute( select(ActiveGroups).where(ActiveGroups.chat_id == str(chat_id)) )
	return q.scalars().one_or_none()


# Get user By Telegram ID
async def user_by_tg_id(user_tg_id: Union[ str, int ], session: Session) -> Optional[User]:
	q = await session.execute( select(User).where(User.user_tg_id == str(user_tg_id)) )
	return q.scalars().one_or_none()


# Get user By Telegram ID
async def get_all_groups(session: Session) -> List[Optional[ActiveGroups]]:
	q = await session.execute( select(ActiveGroups) )
	return q.fetchall()
