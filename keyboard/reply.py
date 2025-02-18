from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def create_keyboard(
    *button: list,
    size: tuple[int] = (2,),
    placeholder: str = None
):
    kb = ReplyKeyboardBuilder()
    for text in button:
        kb.add(KeyboardButton(text=text))

    return kb.adjust(*size).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder)
