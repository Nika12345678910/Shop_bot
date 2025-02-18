import logging
import asyncio
from aiogram import Dispatcher, Bot
from config_data.config import load_config
from handlers.user import user_router
from handlers.admin import admin_router
from middleware.outer import AdminOuterMiddleware, DataBaseSession
from FSM.fsm import storage
from database.engine_db import session_maker, create_db, drop_db


# Что-то новое


logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logging.info('Starting bot')

    config = load_config()

    bot = Bot(token=config.tg_bot.token)
    admin_ids = list(config.tg_bot.admin_ids)
    bot.admin_ids = admin_ids
    dp = Dispatcher(storage=storage)

    async def startup(bot):
        # await drop_db()
        await create_db()

    dp.startup.register(startup)

    dp.include_router(user_router)
    dp.include_router(admin_router)

    admin_router.message.outer_middleware(
        AdminOuterMiddleware(admin_ids=admin_ids))
    dp.update.middleware(DataBaseSession(session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())
