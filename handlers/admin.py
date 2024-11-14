import logging

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, ReplyKeyboardRemove, Message
from aiogram.filters import Command, CommandStart, StateFilter, or_f

from lexicon.lexicon_ru import LEXICON, btns_menu_add_product
from keyboards.reply_kb import create_keyboard
from database.query_orm import (update_image_info_orm,
                                get_categories_orm,
                                add_product_orm,
                                delete_product_orm,
                                get_image_orm,
                                get_product_orm,
                                get_products_orm,
                                update_product_orm,
                                get_all_products_orm,
                                get_info_pages_orm)

from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_kb import get_callback_btns
from FSM.fsm import AddBanner, AddProduct

from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext


admin_router = Router()

logger = logging.getLogger(__name__)
logger.info('Bot in admin handlers')


ADMIN_KB = create_keyboard(
    "Добавить товар",
    "Ассортимент",
    "Добавить/Изменить баннер",
    size=(2,),
    placeholder="Выберите действие"
)


@admin_router.message(Command(commands=["admin"]))
async def get_rights_admin(message: Message):
    await message.answer(text=f'Что хотите сделать?',
                         reply_markup=ADMIN_KB)


#Ассортимент
@admin_router.message(F.text == "Ассортимент")
async def get_products(message: Message, session: AsyncSession):
    categories = await get_categories_orm(session=session)
    button = {category.name: f'CategoryId_{str(category.id)}' for category in categories}
    button["Все"] = "CategoryId_allcategories"
    await message.answer(text="Выберите категорию",
                         reply_markup=get_callback_btns(btns=button))


@admin_router.callback_query(F.data.startswith("CategoryId_"))
async def outpur_products(callback: CallbackQuery, session: AsyncSession):
    CategoryId = callback.data.split('_')[-1]
    if CategoryId=='allcategories':
        products = await get_all_products_orm(session)
    else:
        products = await get_products_orm(session, CategoryId)

    if len(products)==0:
        await callback.answer()
        await callback.message.answer("На данный момент в этой категории нет товаров...\nВыберите другую категорию из перечисленных выше")
        return

    for product in products:
        inline_kb = {
            "Удалить": f"delete_{product.id}",
            "Изменить": f"update_{product.id}"
        }
        await callback.message.answer_photo(photo=product.image,
                                            caption=f'Название: {product.name}\nОписание: {product.description} \nЦена: {product.price}',
                                            reply_markup=get_callback_btns(btns=inline_kb))
    await callback.answer()
    await callback.message.answer("ОК, вот список товаров ⏫")


#Удалить или редактировать товар
@admin_router.callback_query(F.data.startswith("delete_") | F.data.startswith("update_"))
async def delete_update_product(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    product_id = callback.data.split("_")[-1]
    command = callback.data.split("_")[0]
    if command == "delete":
        await delete_product_orm(session, int(product_id))
        await callback.message.answer("Товар удалён")
    else:
        product = await get_product_orm(session, int(product_id))
        AddProduct.product_for_change = product
        await callback.answer()
        await start_add_product(callback.message, state)


#Добавить товар
@admin_router.message(F.text == "Добавить товар", StateFilter(default_state))
async def start_add_product(message: Message, state: FSMContext):
    if AddProduct.product_for_change:
        text = 'Введите название товара или "-" чтобы оставить прежнее'
    else:
        text = 'Введите название товара'
    await message.answer(text='Начинается процесс добавления товара...',
                         reply_markup=ReplyKeyboardRemove())
    await message.answer(text=text,
                         reply_markup=get_callback_btns(btns={"Отмена": "cancel"}))
    await state.set_state(AddProduct.name)


@admin_router.callback_query(F.data == 'cancel')
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddProduct.product_for_change:
        AddProduct.product_for_change = None
    await callback.answer()
    await state.clear()
    await callback.message.answer("Действия отменены", reply_markup=ADMIN_KB)


@admin_router.callback_query(F.data == 'back_step')
async def back_step_handler(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()

    if current_state == AddProduct.name:
        await callback.message.answer(
            text='Предидущего шага нет, или введите название товара или выберите "отмена"',
            reply_markup=get_callback_btns(btns={"Отмена": "cancel"})
        )
        return

    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await callback.answer()
            await state.set_state(previous)
            await callback.message.answer(
                text=f"Ок, вы вернулись к прошлому шагу \n {AddProduct.texts[previous.state]}",
                reply_markup=get_callback_btns(btns=btns_menu_add_product)
            )
            return
        previous = step



@admin_router.message(F.text, AddProduct.name)
async def add_name_product(message: Message, state: FSMContext):
    if AddProduct.product_for_change:
        text = 'Введите описание товара или "-" чтобы оставить прежнее'
    else:
        text = 'Введите описание товара'

    if message.text=='-':
        name = AddProduct.product_for_change.name
    elif 2 >= len(message.text) or len(message.text) >= 150:
        await message.text(text='Название товара не должно превышать 150 символов и должно быть больше 2 символов')
        return
    else:
        name = message.text
    await state.update_data(name=name)
    await message.answer(text, reply_markup=get_callback_btns(btns=btns_menu_add_product))
    await state.set_state(AddProduct.description)


@admin_router.message(F.text, AddProduct.description)
async def add_description_product(message: Message, state: FSMContext, session: AsyncSession):
    if AddProduct.product_for_change:
        text = 'Выберите категорию товара или введите "-" чтобы оставить прежнюю'
    else:
        text = 'Выберите категорию товара'

    if message.text=='-':
        description = AddProduct.product_for_change.description
    elif 5 >= len(message.text) or len(message.text) >= 150:
        await message.answer(text='Описание товара не должно превышать 200 символов и должно быть больше 5 символов')
        return
    else:
        description = message.text
    await state.update_data(description=description)
    categories = await get_categories_orm(session)
    buttons_categories = {category.name: str(category.id) for category in categories}
    await message.answer(text=text,
                         reply_markup=get_callback_btns(btns=buttons_categories))
    await state.set_state(AddProduct.category)


@admin_router.callback_query(AddProduct.category)
async def add_category_product(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    if AddProduct.product_for_change:
        text = 'Введите цену товара или "-" чтобы оставить прежнее'
    else:
        text = 'Введите цену товара'

    if callback.data=='-':
        await callback.answer()
        await state.update_data(category=AddProduct.product_for_change.category_id)
        await callback.message.answer(text=text, reply_markup=get_callback_btns(btns=btns_menu_add_product))
        await state.set_state(AddProduct.price)
    if int(callback.data) in [category.id for category in await get_categories_orm(session)]:
        await callback.answer()
        await state.update_data(category=callback.data)
        await callback.message.answer(text=text, reply_markup=get_callback_btns(btns=btns_menu_add_product))
        await state.set_state(AddProduct.price)
    else:
        await callback.message.answer('Выберите категорию из кнопок ниже',
                                      reply_markup=get_callback_btns(btns=btns_menu_add_product))
        await callback.answer()


@admin_router.message(F.text, AddProduct.price)
async def add_price_product(message: Message, state: FSMContext):
    if AddProduct.product_for_change:
        text = 'Введите картинку или "-" чтобы оставить прежнее'
    else:
        text = 'Введите картинку'

    message_update = message.text.replace('.','').replace(',','')
    if message.text=='-':
        price = AddProduct.product_for_change.price
    elif int(message_update)<=0 and not(message_update.isdigit()):
        await message.answer(text='Цена должна быть больше 0 и содержать только цифры',
                             reply_markup=get_callback_btns(btns=btns_menu_add_product))
        return
    else:
        price = message.text
    await state.update_data(price=price)
    await message.answer(text=text,
                         reply_markup=get_callback_btns(btns=btns_menu_add_product))
    await state.set_state(AddProduct.image)


@admin_router.message(or_f(F.photo, F.text=='-'), AddProduct.image)
async def add_image(message: Message, state: FSMContext, session: AsyncSession):
    if message.text=='-':
        await state.update_data(image=AddProduct.product_for_change.image)
    elif message.photo:
        await state.update_data(image=message.photo[-1].file_id)
    else:
        if AddProduct.product_for_change:
            text = 'Введите картинку или "-" чтобы оставить прежнее'
        else:
            text = 'Введите картинку'
        await message.answer(text=text,
                             reply_markup=get_callback_btns(btns=btns_menu_add_product))
        return

    data = await state.get_data()
    try:
        await add_product_orm(session, data)
        if AddProduct.product_for_change:
            await delete_product_orm(session, AddProduct.product_for_change.id)
            await message.answer("Товар изменён", reply_markup=ADMIN_KB)
        else:
            await message.answer("Товар добавлен", reply_markup=ADMIN_KB)
        await state.clear()

    except Exception as e:
        await message.answer(
            f"Ошибка: \n{str(e)}\nЧто-то пошло не так при добавлении товара в БД",
            reply_markup=ADMIN_KB,
        )
        await state.clear()

    AddProduct.product_for_change = None


@admin_router.message(AddProduct.name)
async def add_name2(message: Message, state: FSMContext):
    await message.answer("Отправьте название товара", reply_markup=get_callback_btns(btns={"Отмена": "cancel"}))


@admin_router.message(AddProduct.description)
async def add_description2(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer("Отправьте описание", reply_markup=get_callback_btns(btns=btns_menu_add_product))


@admin_router.message(AddProduct.price)
async def add_price2(message: Message, state: FSMContext):
    await message.answer("Отправьте цену товара", reply_markup=get_callback_btns(btns=btns_menu_add_product))


@admin_router.message(AddProduct.image)
async def add_name2(message: Message, state: FSMContext):
    await message.answer("Отправьте картинку", reply_markup=get_callback_btns(btns=btns_menu_add_product))


#Добавляем изображение в ImageInfo
@admin_router.message(StateFilter(default_state), F.text == 'Добавить/Изменить баннер')
async def add_image2(message: Message, state: FSMContext, session: AsyncSession):
    pages_names = [page.name for page in await get_info_pages_orm(session)]
    string = "Отправьте фото баннера.\nВ описании укажите для какой страницы:\n"
    for menu_name in pages_names:
        image_bd = await get_image_orm(session, menu_name)
        if image_bd.image:
            string += f"{menu_name} - ✅\n"
        else:
            string += f"{menu_name} - ❌\n"
    await message.answer(text=string)
    await state.set_state(AddBanner.image)


@admin_router.message(AddBanner.image, F.photo)
async def add_banner(message: Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page.name for page in await get_info_pages_orm(session)]
    if for_page not in pages_names:
        await message.answer(f"Введите нормальное название страницы, например:\
                         \n{', '.join(pages_names)}")
        return
    await update_image_info_orm(session, for_page, image_id,)
    await message.answer("Баннер добавлен/изменен.")
    await state.clear()


@admin_router.message(AddBanner.image)
async def add_banner2(message: Message, state: FSMContext):
    await message.answer("Отправьте фото баннера или нажмите отмена",
                         reply_markup=get_callback_btns(btns={"Отмена": "cancel"}))