import asyncio
from sqlalchemy import DateTime, func, select, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from database.models import Base
from config_data.config_db import load_config_db
from lexicon.lexicon_ru import categories, description_for_info_pages
from database.query_orm import add_categories_orm, add_image_info_orm


url = load_config_db().db.create_url()

engine = create_async_engine(url=url, echo=True)
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        await add_categories_orm(session, categories)
        await add_image_info_orm(session, description_for_info_pages)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
