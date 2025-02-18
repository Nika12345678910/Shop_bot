from aiogram import Bot
from config_data.config import load_config
from keyboard.inline import (get_callback_btns, get_menu_kb, get_profile,
                             get_user_catalog_btns,
                             get_user_cart,
                             get_products_btns)
from sqlalchemy.ext.asyncio import AsyncSession
from database.query_orm import (get_image_orm,
                                get_categories_orm, get_product_orm,
                                get_products_orm,
                                delete_from_cart_orm, get_user_orm,
                                reduce_product_in_cart_orm,
                                add_to_cart_orm,
                                get_user_carts_orm)
from aiogram.types import InputMediaPhoto, LabeledPrice
from lexicon.lexicon_ru import Format
from utils.paginator import Paginator


async def create_main_menu(session: AsyncSession, level: int, menu_name: str):
    image_info = await get_image_orm(session, menu_name)
    image = InputMediaPhoto(media=image_info.image,
                            caption=image_info.description)

    kbds = get_menu_kb(level=level)

    return image, kbds


async def create_catalog(session: AsyncSession, level: int, menu_name: str):
    banner = await get_image_orm(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    categories = await get_categories_orm(session)
    kbds = get_user_catalog_btns(level=level, categories=categories)

    return image, kbds


def pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"

    if paginator.has_next():
        btns["След. ▶"] = "next"

    return btns


async def create_products(session: AsyncSession, level: int, category: int, page: int):
    products = await get_products_orm(session, category_id=category)
    if len(products) == 0:
        return 0, 0

    paginator = Paginator(products, page=page)
    product = paginator.get_page()[0]

    image = InputMediaPhoto(
        media=product.image,
        caption=f"Название: {product.product_name}\nОписание: \n{product.description}\n\nСтоимость: {round(product.price, 2)}\n\
                Товар {paginator.page} из {paginator.pages}",
    )

    pagination_btns = pages(paginator)

    kbds = get_products_btns(
        level=level,
        category=category,
        page=page,
        pagination_btns=pagination_btns,
        product_id=product.id,
    )

    return image, kbds


async def create_carts(session: AsyncSession, level: int, menu_name: str, page: int, user_id: int, product_id: int):
    if menu_name == "delete":
        await delete_from_cart_orm(session, user_id, product_id)
        if page > 1:
            page -= 1
    elif menu_name == "decrement":
        is_cart = await reduce_product_in_cart_orm(session, user_id, product_id)
        if page > 1 and not is_cart:
            page -= 1
    elif menu_name == "increment":
        await add_to_cart_orm(session, user_id, product_id)
    elif menu_name:
        pass

    carts = await get_user_carts_orm(session, user_id)

    if not carts:
        image = await get_image_orm(session, "cart")
        image = InputMediaPhoto(
            media=image.image, caption=f"{image.description}"
        )

        kbds = get_user_cart(
            level=level,
            page=None,
            pagination_btns=None,
            product_id=None,
        )

    else:
        # carts - все данные из корзины пользователя (какой продукт и сколько)
        # product_data - данные о продукте
        # cart - данные об одной единице козины

        paginator = Paginator(carts, page=page)

        cart = paginator.get_page()[0]

        cart_price = round(cart.quantity * cart.products_2.price, 2)
        total_price = round(
            sum(cart.quantity * cart.products_2.price for cart in carts), 2
        )
        image = InputMediaPhoto(
            media=cart.products_2.image,
            caption=f"Название: {cart.products_2.product_name}\n\n{cart.products_2.price}руб x {cart.quantity} = {cart_price}руб\
                    \nТовар {paginator.page} из {paginator.pages} в корзине.\n\nОбщая стоимость товаров в корзине {total_price}руб",
        )

        pagination_btns = pages(paginator)

        kbds = get_user_cart(
            level=level,
            page=page,
            pagination_btns=pagination_btns,
            product_id=cart.products_2.id,
        )

    return image, kbds


async def create_profile(session: AsyncSession, level: int, user_id: int, menu_name: str):
    banner = await get_image_orm(session, menu_name)
    user = await get_user_orm(session, user_id)
    profile = Format.format_profile(user.name, user.soname, user.age)
    description = f"{banner.description}\n{profile}"

    image = InputMediaPhoto(media=banner.image, caption=description)
    kbd = get_profile(level=level)

    return image, kbd


async def create_payment(session: AsyncSession, level: int, menu_name: str, user_id: int, bot: Bot):
    carts = await get_user_carts_orm(session, user_id)
    config = load_config()

    total_price = 0
    for cart in carts:
        product_data = await get_product_orm(session, cart.product_id)
        total_price += cart.quantity * product_data.price
    total_price = round(total_price, 2)

    description = f"Сумма к оплате: {total_price}"
    banner = await get_image_orm(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=description)

    PRICE = LabeledPrice(label="Оплата корзины покупок",
                         amount=total_price*100)  # в копейках (руб)

    if config.buy.PayMaster_token.split(':')[1] == 'TEST':
        await bot.send_message(user_id, text="Тестовый платеж!!!")

    try:
        await bot.send_invoice(user_id,
                               title="Оплата покупок",
                               description=description,
                               provider_token=config.buy.PayMaster_token,
                               currency="rub",
                               is_flexible=False,
                               prices=[PRICE],
                               payload="test-invoice-payload")
    except Exception as e:
        media, reply_markup = await base_main_menu(session, level=0, menu_name="main")
        await bot.send_message(user_id,
                               text="Произошла ошибка при отправки платежа. Обратитесь к админу или в тех поддержку")
        await bot.send_photo(media.media, caption=media.caption, reply_markup=reply_markup)

    return 1, 1


async def base_main_menu(
    session: AsyncSession,
    level: int,
    menu_name: str,
    category: int | None = None,
    page: int | None = None,
    product_id: int | None = None,
    user_id: int | None = None,
    bot: Bot | None = None
):
    if level == 0:
        return await create_main_menu(session, level, menu_name)
    elif level == 1:
        return await create_catalog(session, level, menu_name)
    elif level == 2:
        return await create_products(session, level, category, page)
    elif level == 3:
        return await create_carts(session, level, menu_name, page, user_id, product_id)
    elif level == 4:
        return await create_profile(session, level, user_id, menu_name)
    elif level == 5:
        return await create_payment(session, level, menu_name, user_id, bot)
