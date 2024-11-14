from keyboards.inline_kb import (get_menu_kb,
                                 get_user_catalog_btns,
                                 get_user_cart,
                                 get_products_btns)
from sqlalchemy.ext.asyncio import AsyncSession
from database.query_orm import (get_image_orm,
                                get_categories_orm,
                                get_products_orm,
                                delete_from_cart_orm,
                                reduce_product_in_cart_orm,
                                add_to_cart_orm,
                                get_user_carts_orm)
from aiogram.types import InputMediaPhoto
from utils.paginator import Paginator


async def create_main_menu(session, level, menu_name):
    image_info = await get_image_orm(session, menu_name)
    image = InputMediaPhoto(media=image_info.image, caption=image_info.description)

    kbds = get_menu_kb(level=level)

    return image, kbds


async def create_catalog(session: AsyncSession, level: int, menu_name:str):
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
    if len(products)==0:
        return 0, 0

    paginator = Paginator(products, page=page)
    product = paginator.get_page()[0]

    image = InputMediaPhoto(
        media=product.image,
        caption=f"Название: {product.name}\
                Описание: \n{product.description}\n\nСтоимость: {round(product.price, 2)}\n\
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


async def create_carts(session, level, menu_name, page, user_id, product_id):
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
        paginator = Paginator(carts, page=page)

        cart = paginator.get_page()[0]

        cart_price = round(cart.quantity * cart.product.price, 2)
        total_price = round(
            sum(cart.quantity * cart.product.price for cart in carts), 2
        )
        image = InputMediaPhoto(
            media=cart.product.image,
            caption=f"Название: {cart.product.name}\n\n{cart.product.price}руб x {cart.quantity} = {cart_price}руб\
                    \nТовар {paginator.page} из {paginator.pages} в корзине.\n\nОбщая стоимость товаров в корзине {total_price}руб",
        )

        pagination_btns = pages(paginator)

        kbds = get_user_cart(
            level=level,
            page=page,
            pagination_btns=pagination_btns,
            product_id=cart.product.id,
        )

    return image, kbds


async def base_main_menu(
    session: AsyncSession,
    level: int,
    menu_name: str,
    category: int | None = None,
    page: int | None = None,
    product_id: int | None = None,
    user_id: int | None = None,
):
    if level == 0:
        return await create_main_menu(session, level, menu_name)
    elif level == 1:
        return await create_catalog(session, level, menu_name)
    elif level == 2:
        return await create_products(session, level, category, page)
    elif level == 3:
        return await create_carts(session, level, menu_name, page, user_id, product_id)