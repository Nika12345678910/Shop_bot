import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from database.model import Base
from config_data.config import load_config
from database.query_orm import add_image_info_orm
from lexicon.lexicon_ru import description_for_info_pages


logger = logging.getLogger(__name__)
config = load_config()


engine = create_async_engine(url=config.db.connect_sqlite(), echo=True)
session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        await add_image_info_orm(session, description_for_info_pages)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
