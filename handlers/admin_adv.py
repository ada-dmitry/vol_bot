from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select
from database import async_session
from models import User
from uuid import uuid4
import os

router = Router()
admin_ids = list(map(int, os.getenv("ADMINS", "").split(",")))

# Храним рассылки
adv_memory = {}  # {adv_id: {"text": str, "is_active": bool}}
current_adv_id = None

# Состояния для FSM
class AdvForm(StatesGroup):
    short = State()
    full = State()

@router.message(F.text == "/send_adv")
async def start_adv(message: Message, state: FSMContext):
    if message.from_user.id not in admin_ids:
        return await message.answer("⛔ Доступ запрещён.")
    await state.set_state(AdvForm.short)
    await message.answer("Введите краткую форму сообщения:")

@router.message(AdvForm.short)
async def get_short_text(message: Message, state: FSMContext):
    await state.update_data(short=message.text)
    await state.set_state(AdvForm.full)
    await message.answer("Теперь введите полную форму сообщения:")

@router.message(AdvForm.full)
async def get_full_text_and_send(message: Message, state: FSMContext, bot: Bot):
    global current_adv_id, adv_memory

    data = await state.get_data()
    short_text = data["short"]
    full_text = message.text

    # Генерируем уникальный ID рассылки
    adv_id = str(uuid4())

    # Деактивируем старые рассылки
    for adv in adv_memory.values():
        adv["is_active"] = False

    # Сохраняем новую рассылку
    adv_memory[adv_id] = {
        "text": full_text,
        "is_active": True
    }
    current_adv_id = adv_id

    # Клавиатура
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👍 Интересно", callback_data=f"adv:{adv_id}"),
            InlineKeyboardButton(text="👎 Не интересно", callback_data="adv:no")
        ]
    ])

    # Рассылка краткой формы
    async with async_session() as session:
        result = await session.execute(select(User.user_id).where(User.is_subscribed == True))
        users = result.scalars().all()

        sent = 0
        for uid in users:
            try:
                await bot.send_message(uid, short_text, reply_markup=kb)
                sent += 1
            except:
                continue

    await message.answer(f"📬 Рассылка завершена. Отправлено: {sent}")
    await state.clear()
