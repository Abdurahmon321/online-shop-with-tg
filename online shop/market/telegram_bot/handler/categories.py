from telebot import types
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()


from data.loader import bot, ADMIN_ID
from keyboards.inline_buttons import create_inline_buttons
from shop.models import Category


# Django settingslarni sozlash


@bot.message_handler(func=lambda message: message.text == 'Add Category')
def add_category(message):
    if message.from_user.id in ADMIN_ID:
        bot.send_message(message.chat.id, "Please send me the name of the new category.")
        bot.register_next_step_handler(message, save_category)
    else:
        bot.send_message(message.chat.id, "You don't have permission to add categories.")


def save_category(message):
    category_name = message.text
    new_category = Category(name=category_name)
    new_category.save()
    bot.send_message(message.chat.id, f"Category '{category_name}' has been added.")


@bot.message_handler(func=lambda message: message.text == 'Category')
def list_categories(message):
    if message.from_user.id in ADMIN_ID:
        categories = Category.objects.filter(parent__isnull=True)
        buttons = [{'text': category.name, 'callback_data': f'category_{category.id}_{category.name}'} for category in categories]
        buttons.append({'text': 'Add Category', 'callback_data': 'add_category'})
        markup = create_inline_buttons(buttons)
        bot.send_message(message.chat.id, "Categories:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "You don't have permission to view categories.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('category_'))
def show_subcategories(call):
    data = call.data.split('_')
    category_id = data[1]
    category_name = data[2]
    subcategories = Category.objects.filter(parent_id=category_id)
    buttons = [{'text': subcategory.name, 'callback_data': f'subcategory_{subcategory.id}_{subcategory.name}'} for subcategory in subcategories]
    buttons.extend([
        {'text': 'Add Subcategory', 'callback_data': f'add_subcategory_{category_id}'},
        {'text': 'Edit Category', 'callback_data': f'edit_category_{category_id}_{category_name}'},
        {'text': 'Delete Category', 'callback_data': f'delete_category_{category_id}_{category_name}'}
    ])
    markup = create_inline_buttons(buttons)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Category: {category_name}", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('subcategory_'))
def manage_subcategory(call):
    data = call.data.split('_')
    subcategory_id = data[1]
    subcategory_name = data[2]
    buttons = [
        {'text': 'Edit', 'callback_data': f'edit_subcategory_{subcategory_id}_{subcategory_name}'},
        {'text': 'Delete', 'callback_data': f'delete_subcategory_{subcategory_id}_{subcategory_name}'}
    ]
    markup = create_inline_buttons(buttons)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Subcategory: {subcategory_name}", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('add_subcategory_'))
def add_subcategory(call):
    category_id = call.data.split('_')[2]
    bot.send_message(call.message.chat.id, f"Please send me the name of the new subcategory for category {category_id}.")
    bot.register_next_step_handler(call.message, save_subcategory, category_id)


def save_subcategory(message, category_id):
    subcategory_name = message.text
    parent_category = Category.objects.get(id=category_id)
    new_subcategory = Category(name=subcategory_name, parent=parent_category)
    new_subcategory.save()
    bot.send_message(message.chat.id, f"Subcategory '{subcategory_name}' has been added to category {parent_category.name}.")


@bot.callback_query_handler(func=lambda call: call.data == 'add_category')
def add_category_inline(call):
    bot.send_message(call.message.chat.id, "Please send me the name of the new category.")
    bot.register_next_step_handler(call.message, save_category_inline)


def save_category_inline(message):
    category_name = message.text
    new_category = Category(name=category_name)
    new_category.save()
    bot.send_message(message.chat.id, f"Category '{category_name}' has been added.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_category_'))
def edit_category(call):
    data = call.data.split('_')
    category_id = data[2]
    category_name = data[3]
    bot.send_message(call.message.chat.id, f"Please send me the new name for category {category_name}.")
    bot.register_next_step_handler(call.message, update_category, category_id)


def update_category(message, category_id):
    category_name = message.text
    category = Category.objects.get(id=category_id)
    category.name = category_name
    category.save()
    bot.send_message(message.chat.id, f"Category '{category_name}' has been updated.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_category_'))
def confirm_delete_category(call):
    data = call.data.split('_')
    category_id = data[2]
    category_name = data[3]
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Ha", callback_data=f'confirm_delete_category_{category_id}'),
        types.InlineKeyboardButton("Yo'q", callback_data='cancel_delete')
    )
    bot.send_message(call.message.chat.id, f"Category '{category_name}' ni o'chirmoqchimisiz?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_category_'))
def delete_category(call):
    category_id = call.data.split('_')[3]
    category = Category.objects.get(id=category_id)
    category_name = category.name
    category.delete()
    bot.send_message(call.message.chat.id, f"Category '{category_name}' has been deleted.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_subcategory_'))
def edit_subcategory(call):
    data = call.data.split('_')
    subcategory_id = data[2]
    subcategory_name = data[3]
    bot.send_message(call.message.chat.id, f"Please send me the new name for subcategory {subcategory_name}.")
    bot.register_next_step_handler(call.message, update_subcategory, subcategory_id)


def update_subcategory(message, subcategory_id):
    subcategory_name = message.text
    subcategory = Category.objects.get(id=subcategory_id)
    subcategory.name = subcategory_name
    subcategory.save()
    bot.send_message(message.chat.id, f"Subcategory '{subcategory_name}' has been updated.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_subcategory_'))
def confirm_delete_subcategory(call):
    data = call.data.split('_')
    subcategory_id = data[2]
    subcategory_name = data[3]
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Ha", callback_data=f'confirm_delete_subcategory_{subcategory_id}'),
        types.InlineKeyboardButton("Yo'q", callback_data='cancel_delete')
    )
    bot.send_message(call.message.chat.id, f"Subcategory '{subcategory_name}' ni o'chirmoqchimisiz?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_subcategory_'))
def delete_subcategory(call):
    subcategory_id = call.data.split('_')[3]
    subcategory = Category.objects.get(id=subcategory_id)
    subcategory_name = subcategory.name
    subcategory.delete()
    bot.send_message(call.message.chat.id, f"Subcategory '{subcategory_name}' has been deleted.")


@bot.callback_query_handler(func=lambda call: call.data == 'cancel_delete')
def cancel_delete(call):
    bot.send_message(call.message.chat.id, "Mahsulotni o'chirish bekor qilindi.")
