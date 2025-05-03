from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, insert, update
import logging

from models import User
from database import async_session
from keyboards import get_subscription_keyboard

logger = logging.getLogger(__name__)
router = Router()


# Машина состояний
class Register(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_study_group = State()


@router.message(F.text == "/start")
async def start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"User {message.from_user.id} started the bot")
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()

        if user:
            # Приветствие при повторном запуске
            text = (
                f"👋 Привет, {user.full_name or 'друг'}!\n"
                f"Группа: {user.study_group or 'не указана'}\n"
                "Используй кнопки ниже, чтобы управлять подпиской:"
            )
            await message.answer(
                text, reply_markup=get_subscription_keyboard(user.is_subscribed)
            )
        else:
            # Первый запуск — регистрация
            await state.set_state(Register.waiting_for_fullname)
            await message.answer(
                "👋 Привет! Пожалуйста, напиши свои ФИО одной строкой:"
            )


@router.message(Register.waiting_for_fullname)
async def get_fullname(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(Register.waiting_for_study_group)
    await message.answer("Теперь укажи номер своей группы (например, Б11-111):")


@router.message(Register.waiting_for_study_group)
async def get_study_group(message: Message, state: FSMContext):
    data = await state.get_data()
    full_name = data["full_name"]
    study_group = message.text

    async with async_session() as session:
        await session.execute(
            insert(User).values(
                user_id=message.from_user.id,
                full_name=full_name,
                study_group=study_group,
                is_subscribed=True,
            )
        )
        await session.commit()

    await message.answer(
        f"✅ Регистрация завершена!\nФИО: {full_name}\nГруппа: {study_group}"
    )
    await message.answer(
        "Теперь ты можешь управлять подпиской ниже 👇",
        reply_markup=get_subscription_keyboard(True),
    )
    await state.clear()


@router.callback_query(F.data == "subscribe")
async def subscribe(callback: CallbackQuery):
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.user_id == callback.from_user.id)
            .values(is_subscribed=True)
        )
        await session.commit()
    await callback.message.edit_reply_markup(
        reply_markup=get_subscription_keyboard(True)
    )
    await callback.answer("✅ Вы подписались на рассылку!")


@router.callback_query(F.data == "unsubscribe")
async def unsubscribe(callback: CallbackQuery):
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.user_id == callback.from_user.id)
            .values(is_subscribed=False)
        )
        await session.commit()
        await callback.message.edit_reply_markup(
            reply_markup=get_subscription_keyboard(False)
        )
    await callback.answer("❌ Вы отписались от рассылки.")
