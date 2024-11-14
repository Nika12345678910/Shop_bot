from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsAdmin(BaseFilter):
    def __init__(self, admin_password: str) -> None:
        self.admin_password = admin_password

    async def __call__(self, message: Message) -> bool:
        return message.text==self.admin_password