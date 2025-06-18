# run_dev.py
import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# === власні модулі ===
from core.db import init_db
from market.symbols import refresh_futures
from bot.handlers.pairs_parser import router as pairs_router
from core.config import EXCHANGES   # просто щоб перевірити, що імпорт працює

# === TELEGRAM TOKEN ===
# зручніше тримати в змінній оточення (або .env)
from dotenv import load_dotenv
load_dotenv()  

import os
TG_TOKEN = os.getenv("TG_TOKEN")
if TG_TOKEN is None:
    raise RuntimeError("Задайте змінну оточення TG_TOKEN зі своїм Bot API токеном")

# === Логи ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

async def main() -> None:
    # 1) база
    await init_db()

    # 2) планувальник ф'ючерс-символів
    scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")
    scheduler.add_job(refresh_futures, "interval", hours=1, next_run_time=None)
    scheduler.start()

    # 3) Telegram-бот
    bot = Bot(TG_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(pairs_router)

    logging.info("🚀 Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Bot stopped")
