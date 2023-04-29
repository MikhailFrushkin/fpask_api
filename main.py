from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from flask import Flask, request
from loguru import logger

from environs import Env

env = Env()
env.read_env()

application = Flask(__name__)

bot_token_1 = env.str('bot_token_1')
bot_token_2 = env.str('bot_token_2')
bot_1 = Bot(token=bot_token_1)
bot_2 = Bot(token=bot_token_2)
dp_1 = Dispatcher(bot_1)
dp_2 = Dispatcher(bot_2)

WEBHOOK_HOST = "https://mikhailfryshkin.online"
WEBHOOK_PATH = f"/{bot_token_1}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"


@application.route("/")
async def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"


@dp_1.message_handler()
async def handle_message_from_bot_1(message: types.Message):
    await bot_2.send_message(chat_id=message.chat.id, text=message.text)


@dp_2.message_handler()
async def handle_message_from_bot_2(message: types.Message):
    await bot_1.send_message(chat_id=message.chat.id, text=message.text)


async def on_startup(dp):
    await bot_1.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp):
    logger.warning('Shutting down..')
    await bot_1.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()

    logger.warning('Bye!')


@application.route(WEBHOOK_PATH, methods=['POST'])
async def telegram_webhook_1():
    data = await request.get_data()
    update = types.Update.to_object(data)
    print(data)
    await dp_1.process_updates([update])
    return '', 200


@application.route(f'/{bot_token_2}', methods=['POST'])
async def telegram_webhook_2():
    data = await request.get_data()
    update = types.Update.to_object(data)
    await dp_2.process_updates([update])
    return '', 200


if __name__ == '__main__':
    executor.start_webhook(dispatcher=dp_1,
                           webhook_path=WEBHOOK_PATH,
                           on_startup=on_startup,
                           on_shutdown=on_shutdown,
                           skip_updates=True, )
    # executor.start_webhook(dispatcher=dp_2, webhook_path=f'/{bot_token_2}', host=bot_url_2)
    application.run(host='0.0.0.0')
