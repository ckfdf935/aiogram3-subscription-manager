import asyncio
from os import getenv
from dotenv import load_dotenv

from database import init_db
from routers import router
from aiogram import Bot, Dispatcher


load_dotenv()
token = getenv('TOKEN')

dp = Dispatcher()
dp.include_router(router)

async def main():
    bot = Bot(token=token)
    print("Бот запущен")
    await init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
