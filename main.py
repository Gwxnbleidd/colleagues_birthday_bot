import asyncio
from aiogram import Bot,Dispatcher,F

from config import BOT_TOKEN,TUNA_URL
from handlers import router

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__=='__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот завершил работу.')