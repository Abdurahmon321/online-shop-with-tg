from telebot.types import KeyboardButton, ReplyKeyboardMarkup


def admin_keyboard():
    markup = ReplyKeyboardMarkup(row_width=2)
    btn1 = KeyboardButton('Category')
    btn2 = KeyboardButton('Search')
    btn3 = KeyboardButton('Product')
    btn4 = KeyboardButton("Add Product")
    btn5 = KeyboardButton("Add Category")
    btn6 = KeyboardButton("Menu")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup


def user_keyboard():
    markup = ReplyKeyboardMarkup(row_width=1)
    btn1 = KeyboardButton('Search')
    markup.add(btn1)
    return markup