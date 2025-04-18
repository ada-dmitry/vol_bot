from aiogram import Router, F
from aiogram.types import CallbackQuery
from handlers.admin_adv import adv_memory

router = Router()

@router.callback_query(F.data.startswith("adv:"))
async def handle_adv_click(callback: CallbackQuery):
    adv_id = callback.data.split(":")[1]

    adv = adv_memory.get(adv_id)
    if not adv:
        await callback.answer("❌ Сообщение не найдено", show_alert=True)
        return

    if not adv["is_active"]:
        await callback.answer("⏰ Срок действия сообщения истёк", show_alert=True)
        return

    await callback.message.answer(adv["text"])
    await callback.answer("Вот подробности 👇")

@router.callback_query(F.data == "adv:no")
async def handle_not_interested(callback: CallbackQuery):
    await callback.answer("Спасибо за обратную связь!")
