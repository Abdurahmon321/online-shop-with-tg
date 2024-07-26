import requests
from data.loader import bot


@bot.message_handler(content_types=['photo'])
def handle_image(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    file = requests.get(f'https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}')

    if file.status_code == 200:
        # Rasmni yuklash uchun tayyorlash
        files = {'image': (file_info.file_path.split('/')[-1], file.content, 'multipart/form-data')}
        response = requests.post('http://127.0.0.1:8000/api/v1/product-images/', files=files)

        if response.status_code == 201:
            product_info = response.json()
            bot.send_message(message.chat.id,
                             f"Image has been successfully uploaded for product: {product_info['product_name']}\n"
                             f"Description: {product_info['description']}")
        else:
            bot.send_message(message.chat.id, "Failed to upload image.")
    else:
        bot.send_message(message.chat.id, "Failed to retrieve the image from Telegram.")


@bot.message_handler(commands=['get_product'])
def get_product(message):
    response = requests.get('http://127.0.0.1:8000/api/v1/products/')
    if response.status_code == 200:
        products = response.json()
        for product in products:
            bot.send_message(message.chat.id,
                             f"Product Name: {product['name']}\nDescription: {product['description']}")
    else:
        bot.send_message(message.chat.id, "No matching product found.")