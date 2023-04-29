import json

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from environs import Env
from flask import Flask, request, jsonify
from loguru import logger

env = Env()
env.read_env()

application = Flask(__name__)
application.debug = True

bot_token_1 = env.str('bot_token_1')
bot_token_2 = env.str('bot_token_2')
bot_1 = Bot(token=bot_token_1)
bot_2 = Bot(token=bot_token_2)
dp_1 = Dispatcher(bot_1)
dp_2 = Dispatcher(bot_2)

URL1 = "https://api.telegram.org/bot{}/".format(bot_token_1)
URL2 = "https://api.telegram.org/bot{}/".format(bot_token_2)

webhook1 = 'https://api.telegram.org/bot6087228959:AAExcei7wDfKznQEv6jrkAKlTzSIx9Dpu_E/setWebhook?url=https://mikhailfryshkin.ru'
webhook_del = 'https://api.telegram.org/bot6087228959:AAExcei7wDfKznQEv6jrkAKlTzSIx9Dpu_E/deleteWebhook'


def write_json(data, file_name='answer.json'):
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


@application.route("/", methods=['POST', 'GET'])
async def hello():
    if request.method == 'POST':
        try:
            data = request.get_json()
            with open('asdasd.txt', 'w') as f:
                f.write(data)
            logger.info(f"{data}\n")

            chat_id = data['message']['chat']['id']
            message_text = data['message']['text']

            # Отправляем запрос на поиск товара второму боту
            search_result = search_product(message_text, chat_id)

            # Отправляем результаты поиска в чат
            send_message(chat_id, search_result)
            return jsonify(data)
        except Exception as ex:
            logger.debug(ex)
    return f"<h1 style='color:blue'>{request.method}</h1>"


def search_product(product_code, chat_id):
    try:
        url = URL2 + "sendMessage?text={}&chat_id={}".format(product_code, chat_id)
        response = requests.get(url)
        logger.info(f"{url}\n{response.text}")
        search_result = json.loads(response.content)['result']
        write_json(search_result.json(), 'qwe.json')
        return search_result
    except Exception as ex:
        logger.debug(ex)


def send_message(chat_id, text):
    url = URL1 + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    requests.get(url)


if __name__ == '__main__':
    logger.add('info.log', format='{time} {level} {message}')
    application.run(host='0.0.0.0')
