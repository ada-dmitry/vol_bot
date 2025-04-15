from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_subscription_keyboard(subscribed: bool):
    if subscribed:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отписаться", callback_data="unsubscribe")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подписаться", callback_data="subscribe")]
        ])
