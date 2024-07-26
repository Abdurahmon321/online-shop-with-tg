import os
import django
from io import BytesIO
import requests
from telebot import types
from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from django.core.files.base import ContentFile

# Django settingslarni sozlash
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from data.loader import bot, ADMIN_ID
from keyboards.inline_buttons import create_inline_buttons
from shop.models import Product, Category, Brand

CHAT_ID = -1002042393767
BASE_URL = 'http://127.0.0.1:8000'

add_product_data = {}

@bot.message_handler(func=lambda message: message.text == 'Add Product')
def add_product(message):
    if message.from_user.id in ADMIN_ID:
        bot.send_message(message.chat.id, "Maxsulotni nomini kriting:")
        bot.register_next_step_handler(message, get_product_name)
    else:
        bot.send_message(message.chat.id, "Sizda maxsulot qo'shish uchun ruxsat yo'q")

def get_product_name(message):
    if message.text != "Menu":
        chat_id = message.chat.id
        add_product_data[chat_id] = {'name': message.text}
        bot.send_message(chat_id, "Maxsulot haqida tavfsif kiriting!:")
        bot.register_next_step_handler(message, get_product_description)

def get_product_description(message):
    if message.text != "Menu":
        chat_id = message.chat.id
        add_product_data[chat_id]['description'] = message.text
        bot.send_message(chat_id, "Maxsulotni narxini kiritng (faqat sonlar orqali):")
        bot.register_next_step_handler(message, get_product_price)

def get_product_price(message):
    if message.text != "Menu":
        chat_id = message.chat.id
        add_product_data[chat_id]['price'] = message.text
        bot.send_message(chat_id, "Maxsulot sonini kiriting:")
        bot.register_next_step_handler(message, get_product_stock)

def get_product_stock(message):
    if message.text != "Menu":
        chat_id = message.chat.id
        add_product_data[chat_id]['stock'] = message.text
        bot.send_message(chat_id, "Kategoriyani tanlang:")
        send_parent_category_buttons(chat_id)

def send_parent_category_buttons(chat_id):
    categories = Category.objects.filter(parent__isnull=True)
    buttons = [{'text': category.name, 'callback_data': f'parent_category_{category.id}'} for category in categories]
    if buttons:
        markup = create_inline_buttons(buttons)
        bot.send_message(chat_id, "Iltimos, parent kategoriyani tanlang:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Hech qanday parent kategoriya topilmadi.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('parent_category_'))
def get_subcategory_buttons(call):
    chat_id = call.message.chat.id
    parent_category_id = call.data.split('_')[2]
    categories = Category.objects.filter(parent_id=parent_category_id)
    buttons = [{'text': category.name, 'callback_data': f'add_product_category_{category.id}_{category.name}'} for category in categories]
    if buttons:
        markup = create_inline_buttons(buttons)
        bot.send_message(chat_id, "Iltimos, subkategoriyani tanlang:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Hech qanday subkategoriya topilmadi.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('add_product_category_'))
def get_product_category(call):
    chat_id = call.message.chat.id
    data = call.data.split('_')
    category_id = data[3]
    category_name = data[4]
    if chat_id not in add_product_data:
        add_product_data[chat_id] = {}
    add_product_data[chat_id]['category_id'] = category_id
    bot.send_message(chat_id, f"Tanlangan ichki kategoriya: {category_name}. Hozir, mahsulotning brandini tanlang:")
    send_brand_buttons(chat_id)

def send_brand_buttons(chat_id):
    brands = Brand.objects.all()
    buttons = [{'text': brand.name, 'callback_data': f'add_product_brand_{brand.id}_{brand.name}'} for brand in brands]
    if buttons:
        markup = create_inline_buttons(buttons)
        bot.send_message(chat_id, "Brandni tanlang:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Bunday brand mavjud emas")

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_product_brand_'))
def get_product_brand(call):
    chat_id = call.message.chat.id
    data = call.data.split('_')
    brand_id = data[3]
    brand_name = data[4]
    if chat_id not in add_product_data:
        add_product_data[chat_id] = {}
    add_product_data[chat_id]['brand_id'] = brand_id
    bot.send_message(chat_id, f"Tanlangan: {brand_name}. Hozir, Maxsulotni rasmini jo'nating (Hohlagan rasmingizni!):")
    bot.register_next_step_handler_by_chat_id(chat_id, get_product_images)

def get_product_images(message):
    if message.text != "Menu":
        chat_id = message.chat.id
        if 'images' not in add_product_data[chat_id]:
            add_product_data[chat_id]['images'] = []
        if message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            add_product_data[chat_id]['images'].append(ContentFile(downloaded_file, name=f"{file_info.file_path.split('/')[-1]}"))
            bot.send_message(chat_id, "Rasm qabul qilindi. Yana rasm jo'nating yoki tugatish uchun /done ni yozing.")
            bot.register_next_step_handler(message, get_product_images)
        elif message.text == '/done':
            save_product(chat_id)
        else:
            bot.send_message(chat_id, "Please send a photo or type /done to finish.")
            bot.register_next_step_handler(message, get_product_images)


def save_product(chat_id):
    data = add_product_data[chat_id]
    category = Category.objects.get(id=data['category_id'])
    brand = Brand.objects.get(id=data['brand_id'])
    product = Product.objects.create(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        stock=data['stock'],
        category=category,
        brand=brand
    )
    for photo in data['images']:
        product.images.create(image=photo)

    # Mahsulot qo'shildi xabarini yuborish
    bot.send_message(chat_id, f"Maxsulot '{data['name']}' qo'shildi")

    # Ha yoki Yo'q tugmalari bilan inline tugmalar yaratish
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Ha", callback_data=f'confirm_broadcast_{product.id}'))
    markup.add(InlineKeyboardButton("Yo'q", callback_data='cancel_broadcast'))

    bot.send_message(chat_id, "Bu habar guruhga ham yuborilsinmi?", reply_markup=markup)
    del add_product_data[chat_id]


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_broadcast_'))
def confirm_broadcast(call):
    product_id = call.data.split('_')[2]
    product = Product.objects.get(id=product_id)

    # Mahsulot haqida ma'lumot
    caption = (
        f"Nomi: {product.name}\n"
        f"Narxi: {product.price} so'm\n\n"
        f"Ma'lumot: {product.description}\n\n"
        f"Brand: {product.brand.name}\n\n"
        "Ma'lumot yetarli bo'lmagan bo'lsa admin javob berishini kuting! @ne_matulloh_04"
    )

    # Mahsulot rasmlari bilan media group yaratish
    media_group = []
    for index, image in enumerate(product.images.all()):
        image_url = f"{BASE_URL}{image.image.url}"
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            photo = BytesIO(image_response.content)
            if index == 0:
                media_group.append(InputMediaPhoto(photo, caption=caption))
            else:
                media_group.append(InputMediaPhoto(photo))

    # Guruhga xabar yuborish
    bot.send_media_group(CHAT_ID, media_group)
    bot.send_message(call.message.chat.id, "Mahsulot haqida ma'lumot guruhga yuborildi.")


@bot.callback_query_handler(func=lambda call: call.data == 'cancel_broadcast')
def cancel_broadcast(call):
    bot.send_message(call.message.chat.id, "Mahsulot haqida ma'lumot guruhga yuborilmadi.")



@bot.message_handler(func=lambda message: message.text == 'Product')
def list_products(message):
    if message.from_user.id in ADMIN_ID:
        products = Product.objects.all()
        buttons = [{'text': product.name, 'callback_data': f'product_{product.id}_{product.name}'} for product in products]
        buttons.append({'text': 'Add Product', 'callback_data': 'add_product'})
        markup = create_inline_buttons(buttons)
        bot.send_message(message.chat.id, "Products:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Sizda maxsulotlarni ko'rish uchun ruxsat yo'q")


@bot.callback_query_handler(func=lambda call: call.data.startswith('product_'))
def show_product_options(call):
    data = call.data.split('_')
    product_id = data[1]
    product_name = data[2]
    product = Product.objects.get(id=product_id)
    category_name = product.category.name
    brand_name = product.brand.name

    caption = (
        f"Product Name: {product.name}\n"
        f"Product Price: {product.price}\n"
        f"Description: {product.description}\n"
        f"Category: {category_name}\n"
        f"Brand: {brand_name}\n"
    )

    media_group = []
    for index, image in enumerate(product.images.all()):
        image_url = f"{BASE_URL}{image.image.url}"
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            photo = BytesIO(image_response.content)
            if index == 0:
                media_group.append(InputMediaPhoto(photo, caption=caption))
            else:
                media_group.append(InputMediaPhoto(photo))

    if media_group:
        bot.send_media_group(call.message.chat.id, media_group)

    # Create and send buttons
    buttons = [
        {'text': 'Edit', 'callback_data': f'edit_product_{product_id}_{product_name}'},
        {'text': 'Delete', 'callback_data': f'delete_product_{product_id}_{product_name}'},
    ]
    markup = create_inline_buttons(buttons)
    bot.send_message(call.message.chat.id, f"Product: {product_name}", reply_markup=markup)

# Productni yangilash uchun


update_data = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_product_'))
def edit_product(call):
    global update_data
    chat_id = call.message.chat.id
    product_id = call.data.split('_')[2]
    update_data[chat_id] = {'product_id': product_id}
    product = Product.objects.get(id=product_id)
    update_data[chat_id]['current'] = {
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'category': product.category.id,
        'brand': product.brand.id,
        'images': [f"{BASE_URL}{image.image.url}" for image in product.images.all()]
    }
    show_product_info(chat_id)
    bot.send_message(chat_id, "Iltimos, mahsulotning yangi nomini kiriting yoki o'tkazib yuborish uchun /skip ni yuboring:")
    bot.register_next_step_handler(call.message, update_product_name)

def show_product_info(chat_id):
    product_info = update_data[chat_id]['current']
    temp_info = update_data[chat_id].get('temp', {})

    category_id = temp_info.get('category', product_info['category'])
    brand_id = temp_info.get('brand', product_info['brand'])
    category_name = Category.objects.get(id=category_id).name
    brand_name = Brand.objects.get(id=brand_id).name

    caption = (
        f"Product Name: {temp_info.get('name', product_info['name'])}\n"
        f"Product Price: {temp_info.get('price', product_info['price'])}\n"
        f"Description: {temp_info.get('description', product_info['description'])}\n"
        f"Category: {category_name}\n"
        f"Brand: {brand_name}\n"
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
    if media_group:
        bot.send_media_group(chat_id, media_group)

def update_product_name(message):
    global update_data
    if message.text != '/skip':
        update_data[message.chat.id].setdefault('temp', {})['name'] = message.text
    show_product_info(message.chat.id)
    bot.send_message(message.chat.id, "Iltimos, yangi kategoriyani tanlang yoki o'tkazib yuborish uchun /skip ni yuboring:")
    send_update_category_buttons(message.chat.id)

def send_update_category_buttons(chat_id):
    categories = Category.objects.filter(parent__isnull=False)
    buttons = [{'text': category.name, 'callback_data': f'update_product_category_{category.id}_{category.name}'} for category in categories]
    if buttons:
        markup = create_inline_buttons(buttons)
        bot.send_message(chat_id, "Choose a category:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "No subcategories available.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('update_product_category_'))
def update_product_category(call):
    global update_data
    chat_id = call.message.chat.id
    data = call.data.split('_')
    category_id = data[3]
    category_name = data[4]
    if chat_id not in update_data:
        update_data[chat_id] = {}
    update_data[chat_id]['temp'] = update_data[chat_id].get('temp', {})
    update_data[chat_id]['temp']['category'] = category_id
    update_data[chat_id]['temp']['category_name'] = category_name
    show_product_info(chat_id)
    bot.send_message(chat_id, "Iltimos, yangi brendni tanlang yoki o'tkazib yuborish uchun /skip ni yuboring:")
    send_update_brand_buttons(chat_id)

def send_update_brand_buttons(chat_id):
    brands = Brand.objects.all()
    buttons = [{'text': brand.name, 'callback_data': f'update_product_brand_{brand.id}_{brand.name}'} for brand in brands]
    if buttons:
        markup = create_inline_buttons(buttons)
        bot.send_message(chat_id, "Choose a brand:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "No brands available.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('update_product_brand_'))
def update_product_brand(call):
    global update_data
    chat_id = call.message.chat.id
    data = call.data.split('_')
    brand_id = data[3]
    brand_name = data[4]
    if chat_id not in update_data:
        update_data[chat_id] = {}
    update_data[chat_id]['temp'] = update_data[chat_id].get('temp', {})
    update_data[chat_id]['temp']['brand'] = brand_id
    update_data[chat_id]['temp']['brand_name'] = brand_name
    show_product_info(chat_id)
    bot.send_message(chat_id, "Iltimos, yangi narxni kiriting yoki o'tkazib yuborish uchun /skip ni yuboring:")
    bot.register_next_step_handler(call.message, update_product_price)

def update_product_price(message):
    global update_data
    if message.text != '/skip':
        update_data[message.chat.id].setdefault('temp', {})['price'] = message.text
    show_product_info(message.chat.id)
    bot.send_message(message.chat.id, "Iltimos, yangi tavsifni kiriting yoki o'tkazib yuborish uchun /skip ni yuboring:")
    bot.register_next_step_handler(message, update_product_description)

def update_product_description(message):
    global update_data
    if message.text != '/skip':
        update_data[message.chat.id].setdefault('temp', {})['description'] = message.text
    show_product_info(message.chat.id)
    bot.send_message(message.chat.id, "Iltimos, yangi zaxiradagi miqdorni kiriting yoki o'tkazib yuborish uchun /skip ni yuboring:")
    bot.register_next_step_handler(message, update_product_stock)

def update_product_stock(message):
    global update_data
    if message.text != '/skip':
        update_data[message.chat.id].setdefault('temp', {})['stock'] = message.text
    show_product_info(message.chat.id)
    bot.register_next_step_handler(message, update_product_images)


@bot.callback_query_handler(func=lambda call: call.data.startswith('update_product_images_'))
def update_product_images(call):
    chat_id = call.chat.id
    bot.send_message(chat_id, "Maxsulotni rasmini jo'nating (Hohlagan rasmingizni jo'nating) yoki o'tkazib yuborish uchun /skip ni jo'nating:")
    bot.register_next_step_handler_by_chat_id(chat_id, handle_product_images_update)

def handle_product_images_update(message):
    chat_id = message.chat.id
    if 'images' not in update_data[chat_id]['temp']:
        update_data[chat_id]['temp']['images'] = []

    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        update_data[chat_id]['temp']['images'].append(ContentFile(downloaded_file, name=f"{file_info.file_path.split('/')[-1]}"))
        bot.send_message(chat_id, "Rasm qabul qilindi. Yana boshqa rasm jo'nating yoki tugatish uchun /done ni jo'nating.")
        bot.register_next_step_handler(message, handle_product_images_update)
    elif message.text == '/done':
        send_update_product_confirmation(chat_id)
    elif message.text == '/skip':
        send_update_product_confirmation(chat_id)
    else:
        bot.send_message(chat_id, "Rasmni jo'nating yoki tuagtish uchun /done ni jo'nating")
        bot.register_next_step_handler(message, handle_product_images_update)

def send_update_product_confirmation(chat_id):
    global update_data
    data = update_data[chat_id].get('temp', {})
    product_id = update_data[chat_id]['product_id']
    current_data = update_data[chat_id]['current']

    category = Category.objects.get(id=data.get('category', current_data['category']))
    brand = Brand.objects.get(id=data.get('brand', current_data['brand']))

    product = Product.objects.get(id=product_id)
    product.name = data.get('name', current_data['name'])
    product.description = data.get('description', current_data['description'])
    product.price = data.get('price', current_data['price'])
    product.stock = data.get('stock', current_data['stock'])
    product.category = category
    product.brand = brand
    product.save()

    # Rasmlarni yangilash
    if 'images' in data:
        product.images.all().delete()
        for photo in data['images']:
            product.images.create(image=photo)

    bot.send_message(chat_id, "Mahsulot muvaffaqiyatli yangilandi.")
    del update_data[chat_id]


@bot.message_handler(commands=['skip'])
def skip_step(message):
    chat_id = message.chat.id
    if chat_id in update_data:
        next_step_handler = get_next_step_handler(chat_id)
        if next_step_handler:
            bot.register_next_step_handler(message, next_step_handler)
        else:
            send_update_product_confirmation(chat_id)

def get_next_step_handler(chat_id):
    global update_data
    data = update_data[chat_id].get('temp', {})
    if 'name' not in data:
        return update_product_name
    if 'category' not in data:
        return update_product_category
    if 'brand' not in data:
        return update_product_brand
    if 'price' not in data:
        return update_product_price
    if 'description' not in data:
        return update_product_description
    if 'stock' not in data:
        return update_product_stock
    if 'images' not in data:
        return update_product_images
    return None


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_product_'))
def confirm_delete_product(call):
    product_id = call.data.split('_')[2]
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Ha", callback_data=f'confirm_delete_{product_id}'),
        types.InlineKeyboardButton("Yo'q", callback_data='cancel_delete')
    )
    bot.send_message(call.message.chat.id, f"Mahsulotni o'chirmoqchimisiz?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_'))
def delete_product(call):
    product_id = call.data.split('_')[2]
    Product.objects.get(id=product_id).delete()
    bot.send_message(call.message.chat.id, f"Mahsulot {product_id} o'chirildi.")


@bot.callback_query_handler(func=lambda call: call.data == 'cancel_delete')
def cancel_delete(call):
    bot.send_message(call.message.chat.id, "Mahsulotni o'chirish bekor qilindi.")
