import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from lexicon.lexicon_ru import LEXICON
from FSM.fsm import FSMAdminPassword
from config_data.config import load_config
from filter.filter import IsAdmin
from sqlalchemy.ext.asyncio import AsyncSession
from handlers.main_menu import base_main_menu
from keyboards.inline_kb import CallbackMenu, get_callback_btns
from database.query_orm import add_user_orm, add_to_cart_orm


logger = logging.getLogger(__name__)

password_admin = load_config().tg_bot.password_admin
user_router = Router()


@user_router.message(CommandStart())
async def process_start_command(message: Message, session: AsyncSession):
    media, reply_markup = await base_main_menu(session, level=0, menu_name="main")
    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)


@user_router.message(Command(commands=['request_rights']), StateFilter(default_state))
async def process_becomming_admin_command(message: Message, state: FSMContext):
    await message.answer("Пожалуйста введите пароль")
    await state.set_state(FSMAdminPassword.fill_password)


@user_router.message(StateFilter(FSMAdminPassword.fill_password), IsAdmin(password_admin))
async def process_correct_admin_password(message: Message, bot: Bot, state: FSMContext):
    bot.admin_ids += [message.from_user.id]
    await state.clear()
    await message.answer(text=f'{LEXICON["admin"]} {message.from_user.first_name}!')


@user_router.message(StateFilter(FSMAdminPassword.fill_password))
async def process_incorrect_admin_password(message: Message):
    await message.answer(text='Неправильный пароль')
    await state.clear()


async def add_to_cart(callback: CallbackQuery, callback_data: CallbackMenu, session: AsyncSession):
    user = callback.from_user
    await add_user_orm(
        session,
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=None,
    )
    await add_to_cart_orm(session, user_id=user.id, product_id=callback_data.product_id)
    await callback.answer("Товар добавлен в корзину.")


@user_router.callback_query(CallbackMenu.filter())
async def user_menu(callback: CallbackQuery, callback_data: CallbackMenu, session: AsyncSession):

    if callback_data.menu_name == "add_to_cart":
        await add_to_cart(callback, callback_data, session)
        return
    media, reply_markup = await base_main_menu(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category=callback_data.category,
        page=callback_data.page,
        product_id=callback_data.product_id,
        user_id=callback.from_user.id,
    )
    if media==0 and reply_markup==0:
        await callback.answer("В этой категории товаров пока нет...\nВыберите другую")
        return
    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()