import asyncio
from aiogram import Bot,Dispatcher

import os
import sys
sys.path.append(f'{os.getcwd()}')
sys.path.append(f'{os.getcwd()}/db')
sys.path.append(f'{os.getcwd()}/bot')

from config import BOT_TOKEN
from handlers import router

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

async def start_bot():
    await dp.start_polling(bot)

if __name__=='__main__':
#def start_tg_bot():
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print('Бот завершил работу.')