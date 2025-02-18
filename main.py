import asyncio
import logging
from aiogram import Bot, Dispatcher

from database.engine import create_db, drop_db
from config_data.config import load_config
from handler.admin import admin_router
from handler.user import user_router
from middleware.outer import AdminOuterMiddleware, DataBaseSession
from database.engine import session_maker


logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        filename="ru_log.log",
        filemode="w",
        level=logging.DEBUG,
        format="%(filename)s:%(lineno)d #%(levelname)-8s "
               "[%(asctime)s] - %(name)s - %(message)s"
    )

    config = load_config()

    bot = Bot(token=config.tg_bot.token)
    admin_ids = list(config.tg_bot.admin_id)
    bot.admin_ids = admin_ids
    dp = Dispatcher()

    async def startup(bot):
        # await drop_db()
        await create_db()

    dp.startup.register(startup)

    logger.info("Starting bot")
    dp.include_router(user_router)
    dp.include_router(admin_router)

    admin_router.message.outer_middleware(
        AdminOuterMiddleware(admin_ids=admin_ids))
    dp.update.middleware(DataBaseSession(session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
