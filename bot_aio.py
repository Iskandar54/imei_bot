import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.markdown import text
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
import requests
from database import is_user_allowed, add_user_to_whitelist

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADD_WHITELIST = os.getenv('ADD_WHITELIST')
VALID_TOKEN = os.getenv('VALID_TOKEN') # Token для авторизации
API_URL = 'http://127.0.0.1:8000/api/check-imei'


bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

def check_users_whitelist(user_id: int) -> bool:
    if not is_user_allowed(user_id):
        return False
    else:
        return True

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    #print(message.from_user.id)
    if check_users_whitelist(message.from_user.id):
        await message.answer("Привет! Отправь мне IMEI для проверки.")
    else:
        await message.answer("У вас нет доступа к этому боту.")

@dp.message(Command('add'))
async def add_whitelist(message: types.Message):
    await message.answer('Введите Token для добавления в белый лист.')

@dp.message(F.text)
async def handle_message(message: types.Message):
    if message.text != ADD_WHITELIST:
        if not check_users_whitelist(message.from_user.id):
            await message.answer("У вас нет доступа к этому боту.")
            return

        imei = message.text
        try:
            response = requests.post(API_URL, json={"imei": imei, "token": VALID_TOKEN})
            response_data = response.json()
            print(response.status_code)
            if response.status_code == 200 or response.status_code == 201:
                if response_data['status'] == 'success':
                    del response_data['data']["!!! WARNING !!!"] # Удаляет предупреждение что это информация из Sandbox
                    lst = "Информация о IMEI:\n"
                    for i in response_data['data']:
                        if i != 'properties':
                            lst += (i + " : " + str(response_data['data'][i]) + '\n')
                        else:
                            lst += ("Properties - ")
                            for k in response_data['data'][i]:
                                lst += (k + " : " + str(response_data['data'][i][k]) + '\n')
                    await message.answer(lst)
                else:
                    await message.answer(f"Ошибка: {response_data['message']}")
            else:
                await message.answer("Произошла ошибка при проверке IMEI.")
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            await message.answer("Произошла внутренняя ошибка при обработке запроса.")
    else:
        add_user_to_whitelist(message.from_user.id)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())