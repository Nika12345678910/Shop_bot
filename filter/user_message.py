from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from lexicon.lexicon_ru import description_for_info_pages
from database.query_orm import get_image_orm


class NameFilter(BaseFilter):
    async def __call__(self, message: Message):
        for i in message.text:
            if 1040 > ord(i) or ord(i) > 1103:
                return False
        return True


class AgeFilter(BaseFilter):
    async def __call__(self, message: Message):
        if message.text.isdigit():
            if 0 < int(message.text) <= 100:
                return True
            return False
        return False


class AddedImageInfoFilter(BaseFilter):
    async def __call__(self, message: Message, session: AsyncSession):
        for page, description in description_for_info_pages.items():
            banner = await get_image_orm(session, page)
            if banner.image == None:
                await message.answer("Картинки для меню еще не добавлены. Магазин в процессе настройки")
                return False
        return True
