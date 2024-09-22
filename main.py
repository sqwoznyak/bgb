from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode  
from aiogram.client.default import DefaultBotProperties 
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router
import asyncio
import logging

async def main():
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
