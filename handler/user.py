from imaplib import Commands
import logging

from aiogram import Bot, Router, F
from aiogram.filters import CommandStart, StateFilter, or_f
from aiogram.types import Message, CallbackQuery, ContentType, PreCheckoutQuery
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from config_data.config import load_config
from handler.main_menu import base_main_menu
from lexicon.lexicon_ru import bot_message, button
from database.query_orm import (add_to_cart_orm, get_products_orm, get_user_orm,
                                add_user_orm,
                                get_categories_orm)
from keyboard.inline import CallbackMenu, get_callback_btns
from FSM.fsm import RegistrationFSM
from filter.user_message import NameFilter, AgeFilter, AddedImageInfoFilter


user_router = Router()
logger = logging.getLogger(__name__)


@user_router.message(or_f(CommandStart(),  F.text == "Главное меню"), AddedImageInfoFilter())
async def start_command(message: Message, session: AsyncSession):
    user = await get_user_orm(session, message.from_user.id)
    if user:
        # вывод пользователю главное меню (категории, профиль, козина)
        media, reply_markup = await base_main_menu(session, level=0, menu_name="main")
        await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)
        return
    await message.answer(text=bot_message["nessesary_regestration"],
                         reply_markup=get_callback_btns(btns=button["reg_button"]))


###    Регистрация    ###


@user_router.callback_query(F.data == "registration", StateFilter(None))
async def starting_registration_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer(text=bot_message["starting_registration"])
    await callback.message.answer(text=bot_message["enter_name"])
    await state.set_state(RegistrationFSM.name)


@user_router.message(RegistrationFSM.name, NameFilter())
async def get_name_command(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer(text=bot_message["enter_soname"])
    await state.set_state(RegistrationFSM.soname)


@user_router.message(RegistrationFSM.soname, NameFilter())
async def get_soname_command(message: Message, state: FSMContext):
    soname = message.text
    await state.update_data(soname=soname)
    await message.answer(text=bot_message["enter_age"])
    await state.set_state(RegistrationFSM.age)


@user_router.message(RegistrationFSM.age, AgeFilter())
async def get_age_command(message: Message, state: FSMContext, session: AsyncSession):
    age = message.text
    await state.update_data(age=age)

    data = await state.get_data()

    try:
        await add_user_orm(user_id=message.from_user.id,
                           name=data["name"],
                           soname=data["soname"],
                           age=data["age"],
                           session=session)
        await state.clear()
        await message.answer(text=bot_message["registration_successful"])
        media, reply_markup = await base_main_menu(session, level=0, menu_name="main")
        await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)

    except Exception as e:
        await message.answer(
            f"Ошибка: \n{str(e)}\nЧто-то пошло не так при добавлении товара в БД",
            reply_markup=get_callback_btns(btns=button["main_menu"]))
        await state.clear()


@user_router.message(RegistrationFSM.name)
async def get_name_command(message: Message):
    await message.answer(text=bot_message["error_enter_name"])


@user_router.message(RegistrationFSM.soname)
async def get_soname_command(message: Message):
    await message.answer(text=bot_message["error_enter_soname"])


@user_router.message(RegistrationFSM.age)
async def get_age_command(message: Message):
    await message.answer(text=bot_message["error_enter_age"])


###    Каталог товаров    ###


async def add_to_cart(callback: CallbackQuery, callback_data: CallbackMenu, session: AsyncSession):
    try:
        await add_to_cart_orm(session, user_id=callback.from_user.id, product_id=callback_data.product_id)
        await callback.answer("Товар добавлен в корзину.")
    except Exception as e:
        await callback.message(f"Возникла ошибка при добавлении товара в корзмеу: \n{e}")


@user_router.callback_query(CallbackMenu.filter())
async def user_menu(callback: CallbackQuery, callback_data: CallbackMenu, session: AsyncSession, bot: Bot):
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
        bot=bot
    )
    if media == 0 and reply_markup == 0:
        await callback.answer("В этой категории товаров пока нет...\nВыберите другую")
        return
    if media == 1 and reply_markup == 1:
        return
    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()


@user_router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)
    logging.info(
        f"PreCheckoutQuery ID: {pre_checkout_q.id}, Payload: {pre_checkout_q.invoice_payload}")


@user_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message, session: AsyncSession):
    logging.info("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment
    logging.info(f"Payment info: {payment_info}")

    payload = payment_info.invoice_payload
    logging.info(f"Invoice payload: {payload}")

    user_id = message.from_user.id

    # Важно: Проверяйте, что платеж действительно пришел от PayMaster!
    # Лучше всего делать это через API PayMaster (верификация транзакции).
    # Этот пример НЕ реализует верификацию!
    # Просто показывает, как получить данные.

    await message.answer(
        f"Спасибо за оплату!  Вы приобрели наш супер-товар. ID платежа: {payment_info.telegram_payment_charge_id}",
    )
    media, reply_markup = await base_main_menu(session, level=0, menu_name="main")
    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)
