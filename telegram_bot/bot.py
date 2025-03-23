from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from telegram_bot.config import settings
from telegram_bot.handlers import case_handler, desk_handler
from telegram_bot.utils.logger import logger

async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем хендлеры
    dp.include_router(case_handler.router)
    dp.include_router(desk_handler.router)

    logger.info("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
