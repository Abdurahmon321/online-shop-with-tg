from io import BytesIO
import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()


from telebot.types import Message, InputMediaPhoto
from data.loader import bot, ADMIN_ID
from keyboards.buttons import admin_keyboard, user_keyboard
from keyboards.inline_buttons import create_inline_buttons
from shop.models import Category, Brand

# Django settingslarni sozlash
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

BASE_URL = 'http://127.0.0.1:8000'


@bot.message_handler(commands=['start'])
def start(message: Message):
    print("---------------------------------------------")
    print(message.from_user.id)
    print("---------------------------------------------")
    if message.from_user.id in ADMIN_ID:
        bot.send_message(message.chat.id, "Welcome, Admin!", reply_markup=admin_keyboard())
    else:
        bot.send_message(message.chat.id, "7/7 do'kon botiga hush kelibsiz!\n"
                                          "Bu yerda do'konimizdagi maxsulotlarni rasm yoki nomi orqali qidirishingiz mumkin!"
                                          "Rasmni jo'nating yoki search bo'limini ishga tushririb maxsulotni nomini kiriting!"
                                          "Botning ishlashida hatolikni sezsangiz /help buyrug'ini ishga tushiring", reply_markup=user_keyboard())


@bot.message_handler(func=lambda message: message.text == 'Search')
def search(message):
    if message.chat.id <= 0:
        bot.send_message(message.chat.id, "Guruh azolariga halaqt qilmaslig uchun botning chatida ham maxsulotni qidirishingiz mumkin! 👉@shop_7_7_bot")
    bot.send_message(message.chat.id, "Iltimos qidirayotgan maxsulotingizni nomini kiriting!")
    bot.register_next_step_handler(message, perform_search)


def perform_search(message):
    search_query = message.text
    response = requests.get(f'{BASE_URL}/api/v1/search/', params={'q': search_query})
    if response.status_code == 200:
        products = response.json()
        if products:
            for product in products:
                category = Category.objects.get(id=product['category'])
                brand = Brand.objects.get(id=product['brand'])

                caption = (
                    f"Nomi: {product['name']}\n"
                    f"Narxi: {product['price']} so'm\n\n"
                    f"Ma'lumot: {product['description']}\n\n"
                    # f"Category: {category.name}\n"
                    f"Brand: {brand.name}\n"
                )
                media_group = []
                for index, image in enumerate(product['images']):
                    image_url = f"{image['image']}"
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        photo = BytesIO(image_response.content)
                        if index == 0:
                            media_group.append(InputMediaPhoto(photo, caption=caption))
                        else:
                            media_group.append(InputMediaPhoto(photo))

                if media_group:
                    bot.send_media_group(message.chat.id, media_group)

                if message.from_user.id in ADMIN_ID:
                    buttons = [
                        {'text': 'Edit', 'callback_data': f'edit_product_{product["id"]}_{product["name"]}'},
                        {'text': 'Delete', 'callback_data': f'delete_product_{product["id"]}_{product["name"]}'}
                    ]
                    markup = create_inline_buttons(buttons)
                    bot.send_message(message.chat.id, f"Manage Product: {product['name']}", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "No matching products found.")
    else:
        bot.send_message(message.chat.id, "Failed to search for products.")


@bot.message_handler(commands=['help'])
def help(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Botdagi hatolik yuzasidan @abdurahmon_8847 ga murojat qiling")
