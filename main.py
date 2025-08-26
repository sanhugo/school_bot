import asyncio
from aiogram import Bot, Dispatcher
from app.handlers import router


async def main():
    bot = Bot(token="6947641516:AAFcdESFQCN78OS7eRlzPMW7luuI5k0-qVQ")
    dp  = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        print('Bot enabled')
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot is disabled')