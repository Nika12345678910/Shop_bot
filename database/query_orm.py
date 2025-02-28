from sqlalchemy import update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.model import ImageInfoORM, PaymentInfoORM, UserORM, CatalogORM, CategoryORM, ShoppingCartORM


async def get_user_orm(session: AsyncSession, user_id: int):
    query = select(UserORM).where(UserORM.user_id == user_id)
    result = await session.execute(query)
    return result.scalar()


# User

async def add_user_orm(user_id: int,
                       name: str,
                       soname: str,
                       age: int,
                       session: AsyncSession):
    session.add(
        UserORM(user_id=user_id, name=name, soname=soname, age=age)
    )
    await session.commit()


# Category

async def add_categories_orm(session: AsyncSession, data: list):
    query = select(CategoryORM)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([CategoryORM(title=name)
                    for name in data])
    await session.commit()


async def get_categories_orm(session: AsyncSession):
    query = select(CategoryORM)
    result = await session.execute(query)
    return result.scalars().all()


# Catalog

async def add_product_orm(session: AsyncSession, data: dict):
    obj = CatalogORM(
        product_name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],
        category_id=int(data["category"]),
    )
    session.add(obj)
    await session.commit()


async def get_products_orm(session: AsyncSession, category_id):
    query = select(CatalogORM).where(
        CatalogORM.category_id == int(category_id))
    result = await session.execute(query)
    return result.scalars().all()


async def get_all_products_orm(session: AsyncSession):
    query = select(CatalogORM)
    result = await session.execute(query)
    return result.scalars().all()


async def get_product_orm(session: AsyncSession, product_id: int):
    query = select(CatalogORM).where(CatalogORM.id == product_id)
    result = await session.execute(query)
    return result.scalar()


async def update_product_orm(session: AsyncSession, product_id: int, data: dict):
    query = (update(CatalogORM).where(CatalogORM.id == product_id).values(
        product_name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],
        category_id=int(data["category"]),
    ))
    await session.execute(query)
    await session.commit()


async def delete_product_orm(session: AsyncSession, product_id: int):
    query = delete(CatalogORM).where(CatalogORM.id == product_id)
    await session.execute(query)
    await session.commit()


###    ImageInfo   ###


async def add_image_info_orm(session: AsyncSession, data: dict):
    query = select(ImageInfoORM)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([ImageInfoORM(name=name, description=description)
                    for name, description in data.items()])
    await session.commit()


async def update_image_info_orm(session: AsyncSession, name, image):
    query = update(ImageInfoORM).where(
        ImageInfoORM.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


async def get_image_orm(session: AsyncSession, page: str):
    query = select(ImageInfoORM).where(ImageInfoORM.name == page)
    result = await session.execute(query)
    return result.scalar()


async def get_info_pages_orm(session: AsyncSession):
    query = select(ImageInfoORM)
    result = await session.execute(query)
    return result.scalars().all()


###    Shopping Cart    ###


async def add_to_cart_orm(session: AsyncSession, user_id: int, product_id: int):
    query = select(ShoppingCartORM).where(ShoppingCartORM.user_id == user_id,
                                          ShoppingCartORM.product_id == product_id)
    cart = await session.execute(query)
    cart = cart.scalar()
    if cart:
        cart.quantity += 1
        await session.commit()
        return cart
    else:
        session.add(ShoppingCartORM(user_id=user_id,
                    product_id=product_id, quantity=1))
        await session.commit()


async def get_user_carts_orm(session: AsyncSession, user_id: int):
    query = query = select(ShoppingCartORM).filter(
        ShoppingCartORM.user_id == user_id).options(joinedload(ShoppingCartORM.products_2))
    result = await session.execute(query)
    return result.scalars().all()


async def delete_from_cart_orm(session: AsyncSession, user_id: int, product_id: int):
    query = delete(ShoppingCartORM).where(ShoppingCartORM.user_id == user_id,
                                          ShoppingCartORM.product_id == product_id)
    await session.execute(query)
    await session.commit()


async def reduce_product_in_cart_orm(session: AsyncSession, user_id: int, product_id: int):
    query = select(ShoppingCartORM).where(ShoppingCartORM.user_id == user_id,
                                          ShoppingCartORM.product_id == product_id)
    cart = await session.execute(query)
    cart = cart.scalar()

    if not cart:
        return
    if cart.quantity > 1:
        cart.quantity -= 1
        await session.commit()
        return True
    else:
        await delete_from_cart_orm(session, user_id, product_id)
        await session.commit()
        return False


###    Payment info    ###


async def add_payment(session: AsyncSession,
                      user_id: int,
                      product_id: int,
                      quantity: int,
                      payment_sum: int):
    session.add(
        PaymentInfoORM(
            user_id=user_id, product_id=product_id,
            quantity=quantity, payment_sum=payment_sum))
    await session.commit()
