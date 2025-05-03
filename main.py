from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import asyncio
import os
from dotenv import load_dotenv
import logging


from handlers import user, admin, admin_adv, adv_callbacks
from database import engine, Base

load_dotenv()

logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),  # Логирование в файл bot.log
        # logging.StreamHandler(),  # Логирование в консоль
    ],
)
logger = logging.getLogger(__name__)


async def on_startup():
    """
    Основная процедура для запуска работы с БД чреез SQLAlchemy.
    """
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Сброс БД
        await conn.run_sync(Base.metadata.create_all)


async def main():
    """
    Функция запуска бота, подключение к TG_API, создание диспетчера, подключение роутеров и запуск бота в режиме пуллинг.
    """
    bot = Bot(token=os.getenv("BOT_TOKEN"))  # type: ignore
    dp = Dispatcher(storage=MemoryStorage())
    logger.info("Запуск работы бота.")
    dp.include_routers(
        user.router, admin.router, admin_adv.router, adv_callbacks.router
    )
    await on_startup()
    await dp.start_polling(bot)  # Бот в пуллинг режиме - "почтальон для API"


if __name__ == "__main__":
    asyncio.run(main())
