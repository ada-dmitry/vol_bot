from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, insert, update
from models import User
from database import async_session
from keyboards import get_subscription_keyboard

router = Router()

@router.message(F.text == "/start")
async def start_handler(message: Message):
    async with async_session() as session:

        result = await session.execute(select(User).where(User.user_id == message.from_user.id))
        user = result.scalar_one_or_none()
        if not user:
            await session.execute(insert(User).values(user_id=message.from_user.id))
            await session.commit()
        text = "Добро пожаловать! Управляйте подпиской:"
        await message.answer(text, reply_markup=get_subscription_keyboard(user.is_subscribed if user else True))

@router.callback_query(F.data.in_(["subscribe", "unsubscribe"]))
async def toggle_subscription(callback: CallbackQuery):
    subscribe = callback.data == "subscribe"
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.user_id == callback.from_user.id)
            .values(is_subscribed=subscribe)
        )
        await session.commit()
    await callback.message.edit_reply_markup(reply_markup=get_subscription_keyboard(subscribe))
    await callback.answer("Вы подписались!" if subscribe else "Вы отписались.")
