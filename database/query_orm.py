import math
import logging
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from database.models import ImageInfo, Cart, Category, Product, User


#User
async def add_user_orm(
    session: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            User(user_id=user_id, first_name=first_name, last_name=last_name, phone=phone)
        )
        await session.commit()


#Product
async def add_product_orm(session: AsyncSession, data: dict):
    obj = Product(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],
        category_id=int(data["category"]),
    )
    session.add(obj)
    await session.commit()


async def get_products_orm(session: AsyncSession, category_id):
    query = select(Product).where(Product.category_id == int(category_id))
    result = await session.execute(query)
    return result.scalars().all()


async def get_all_products_orm(session: AsyncSession):
    query = select(Product)
    result = await session.execute(query)
    return result.scalars().all()


async def get_product_orm(session: AsyncSession, product_id: int):
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    return result.scalar()


async def update_product_orm(session: AsyncSession, product_id: int, data):
    query = (
        update(Product)
        .where(Product.id == product_id)
        .values(
            name=data["name"],
            description=data["description"],
            price=float(data["price"]),
            image=data["image"],
            category_id=int(data["category"]),
        )
    )
    await session.execute(query)
    await session.commit()


async def delete_product_orm(session: AsyncSession, product_id: int):
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()


#Cart
async def add_to_cart_orm(session: AsyncSession, user_id: int, product_id: int):
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    cart = await session.execute(query)
    cart = cart.scalar()
    if cart:
        cart.quantity += 1
        await session.commit()
        return cart
    else:
        session.add(Cart(user_id=user_id, product_id=product_id, quantity=1))
        await session.commit()



async def get_user_carts_orm(session: AsyncSession, user_id):
    query = select(Cart).filter(Cart.user_id == user_id).options(joinedload(Cart.product))
    result = await session.execute(query)
    return result.scalars().all()


async def delete_from_cart_orm(session: AsyncSession, user_id: int, product_id: int):
    query = delete(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    await session.execute(query)
    await session.commit()


async def reduce_product_in_cart_orm(session: AsyncSession, user_id: int, product_id: int):
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    cart = await session.execute(query)
    cart = cart.scalar()

    if not cart:
        return
    if cart.quantity > 1:
        cart.quantity -= 1
        await session.commit()
        return True
    else:
        await orm_delete_from_cart(session, user_id, product_id)
        await session.commit()
        return False


#ImageInfo
async def add_image_info_orm(session: AsyncSession, data: dict):
    query = select(ImageInfo)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([ImageInfo(name=name, description=description)
                    for name, description in data.items()])
    await session.commit()


async def update_image_info_orm(session: AsyncSession, name, image):
    query = update(ImageInfo).where(ImageInfo.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


async def get_image_orm(session: AsyncSession, page: str):
    query = select(ImageInfo).where(ImageInfo.name == page)
    result = await session.execute(query)
    return result.scalar()


async def get_info_pages_orm(session: AsyncSession):
    query = select(ImageInfo)
    result = await session.execute(query)
    return result.scalars().all()


#Category
async def add_categories_orm(session: AsyncSession, data: list):
    query = select(Category)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Category(name=name)
                    for name in data])
    await session.commit()


async def get_categories_orm(session: AsyncSession):
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()
