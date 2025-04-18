from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import asyncio
import os
from dotenv import load_dotenv

from handlers import user, admin, admin_adv, adv_callbacks
from database import engine, Base
load_dotenv()



async def on_startup():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Сброс БД
        await conn.run_sync(Base.metadata.create_all)

async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(
        user.router,
        admin.router,
        admin_adv.router,
        adv_callbacks.router
    )
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

