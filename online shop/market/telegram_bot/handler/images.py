import os
import django
from telebot import TeleBot, types

# Django settingslarni sozlash
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()
from django.db.models import Count
import requests

from telebot.types import Message, InputMediaPhoto
from io import BytesIO
from shop.models import Telegram_User
from data.loader import bot, ADMIN_ID


@bot.message_handler(content_types=['photo'])
def handle_image(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    file = requests.get(f'https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}')

    response = requests.post('http://127.0.0.1:8000/api/v1/product-images/compare/', files={'image': file.content})

    if response.status_code == 200:
        product_info = response.json()
        caption = (
            f"Nomi: {product_info['name']}\n"
            f"Narxi: {product_info['product_price']}so'm\n\n"
            f"Ma'lumot: {product_info['description']}\n\n"
            # f"Category: {product_info['product_category']}\n"
            f"Brand: {product_info['product_brand']}\n\n"
            "Ma'lumot yetarli bo'lmagan bo'lsa admin javob berishini kuting! @ne_matulloh_04"
        )

        media_group = []
        for index, image_url in enumerate(product_info['images']):
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                photo = BytesIO(image_response.content)
                if index == 0:
                    media_group.append(InputMediaPhoto(photo, caption=caption))
                else:
                    media_group.append(InputMediaPhoto(photo))

        bot.send_media_group(message.chat.id, media_group)
    else:
        bot.send_message(message.chat.id, "Maxsulot topilmadi!. Admin javob berishini kuting!")


@bot.message_handler(func=lambda message: message.reply_to_message is not None and message.reply_to_message.photo)
def reply_handler(message):
    print("---------------------------------------------------------------------")
    print(message)
    print("---------------------------------------------------------------------")
    replied_to = message.reply_to_message
    file_info = bot.get_file(replied_to.photo[-1].file_id)
    file = requests.get(f'https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}')
    response = requests.post('http://127.0.0.1:8000/api/v1/product-images/compare/', files={'image': file.content})

    if response.status_code == 200:
        product_info = response.json()
        caption = (
            f"Nomi: {product_info['name']}\n"
            f"Narxi: {product_info['product_price']} so'm\n\n"
            f"Ma'lumot: {product_info['description']}\n\n"
            # f"Category: {product_info['product_category']}\n"
            f"Brand: {product_info['product_brand']}\n\n"
            "Ma'lumot yetarli bo'lmagan bo'lsa admin javob berishini kuting! @ne_matulloh_04"
        )

        media_group = []
        for index, image_url in enumerate(product_info['images']):
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                photo = BytesIO(image_response.content)
                if index == 0:
                    media_group.append(InputMediaPhoto(photo, caption=caption))
                else:
                    media_group.append(InputMediaPhoto(photo))

        bot.send_media_group(message.chat.id, media_group)
    else:
        bot.send_message(message.chat.id, "Maxsulot topilmadi!. Admin javob berishini kuting!")


@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        username = new_member.username or "Noma'lum"
        first_name = new_member.first_name or "Noma'lum"
        added_by = message.from_user.username or "Noma'lum"

        Telegram_User.objects.create(
            first_name=first_name,
            username=username,
            added_by=added_by
        )

        welcome_text = (f"Assalomu alaykum, @{username}!\n\n"
                        "Guruhimizga xush kelibsiz!\n\n"
                        "Qidirayotgan mahsulotingizni rasmini tashlang yoki botdan foydalaning 👉@shop_7_7_bot")
        bot.send_message(message.chat.id, welcome_text)


@bot.message_handler(commands=['leaderboard'])
def leaderboard(message):
    if message.from_user.id in ADMIN_ID:
        bot.delete_message(message.chat.id, message.message_id)
        leaders = Telegram_User.objects.values('added_by').annotate(count=Count('added_by')).order_by('-count')[:10]
        leaderboard_text = "Kim ko'p odam qo'shgan:\n\n"
        for leader in leaders:
            leaderboard_text += f"@{leader['added_by']}: {leader['count']} ta odam\n"
        bot.send_message(message.chat.id, leaderboard_text)
    else:
        bot.send_message(message.chat.id, "Sizda bu komandani ishlatish uchun ruxsat yo'q.")

