from aiogram import Router, F, Bot
from aiogram.types import Message
from sqlalchemy import select
from models import User
from database import async_session
import os

router = Router()
admin_ids = list(map(int, os.getenv("ADMINS").split(",")))

@router.message(F.text == "/admin")
async def admin_panel(message: Message):
    if message.from_user.id not in admin_ids:
        return await message.answer("Доступ запрещён.")
    await message.answer("Команды:\n/stat — статистика\n/broadcast <текст> — рассылка")

@router.message(F.text.startswith("/stat"))
async def stat_handler(message: Message):
    if message.from_user.id not in admin_ids:
        return
    async with async_session() as session:
        total = await session.scalar(select(User).count())
        subscribed = await session.scalar(select(User).where(User.is_subscribed).count())
    await message.answer(f"Всего пользователей: {total}\nПодписаны: {subscribed}")

@router.message(F.text.startswith("/broadcast "))
async def broadcast_handler(message: Message, bot: Bot):
    if message.from_user.id not in admin_ids:
        await message.answer("Доступ запрещён.")
        return

    text = message.text.removeprefix("/broadcast ").strip()
    if not text:
        await message.answer("Текст рассылки не найден.")
        return

    sent = 0
    failed = 0

    async with async_session() as session:
        result = await session.execute(select(User.user_id).where(User.is_subscribed))
        users = result.scalars().all()

        for uid in users:
            try:
                await bot.send_message(uid, text)
                sent += 1
            except Exception:
                failed += 1

    await message.answer(f"📬 Рассылка завершена:\nУспешно: {sent}\nОшибок: {failed}")