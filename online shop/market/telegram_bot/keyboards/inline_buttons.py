from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot import types


def create_inline_buttons(buttons):
    markup = types.InlineKeyboardMarkup()
    for button in buttons:
        markup.add(types.InlineKeyboardButton(text=button['text'], callback_data=button['callback_data']))
    return markup
