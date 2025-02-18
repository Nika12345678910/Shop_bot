from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import DateTime, func, BigInteger, String, ForeignKey, Text


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now())


class ShoppingCartORM(Base):
    __tablename__ = "Shopping cart"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, autoincrement=True, unique=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("User.id", ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("Catalog.id", ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)

    products_2 = relationship("CatalogORM", back_populates="shopping_carts_2")
    users = relationship("UserORM", back_populates="shopping_carts_1")


class PaymentInfoORM(Base):
    __tablename__ = "Payment info"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("User.id", ondelete='CASCADE'), nullable=False)
    payment_sum: Mapped[int] = mapped_column(nullable=False)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("Catalog.id", ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)

    product_3 = relationship(
        "CatalogORM", back_populates="payments")
    user = relationship("UserORM", back_populates="payments")


class UserORM(Base):
    __tablename__ = "User"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, autoincrement=True, unique=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    soname: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)

    shopping_carts_1 = relationship(
        "ShoppingCartORM", back_populates="users", foreign_keys=[ShoppingCartORM.user_id])
    payments = relationship("PaymentInfoORM", back_populates="user", foreign_keys=[
                            PaymentInfoORM.user_id])


class CatalogORM(Base):
    __tablename__ = "Catalog"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, autoincrement=True, unique=True)
    product_name: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("Category.id", ondelete='CASCADE'), nullable=False)
    image: Mapped[str] = mapped_column(nullable=False)

    shopping_carts_2 = relationship(
        "ShoppingCartORM", back_populates="products_2", foreign_keys=[ShoppingCartORM.product_id])
    titls = relationship("CategoryORM", back_populates="products_1")
    payments = relationship("PaymentInfoORM", back_populates="product_3", foreign_keys=[
                            PaymentInfoORM.product_id])


class CategoryORM(Base):
    __tablename__ = "Category"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, autoincrement=True, unique=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)

    products_1 = relationship("CatalogORM", back_populates="titls", foreign_keys=[
                              CatalogORM.category_id])


class ImageInfoORM(Base):
    __tablename__ = 'Image info'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(15), unique=True)
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)


'''
Уточнение по коду:
1. String(int) - задает кол-во символов, которые можно поместить в ячейку
2. BigInteger - нужен, чтоб не возникало ошибок при сохранении телеграмм ид юзера (есть ид, которые превышают 2 байта)
'''
