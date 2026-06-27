import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

import database
from ai_handlers import generate_daily_motivation
from bot import dp, bot

logging.basicConfig(level=logging.INFO)

async def reset_message_counts_task():
    """Scheduled task to reset all message counts."""
    logging.info("Running daily message count reset...")
    database.reset_all_message_counts()
    logging.info("Message counts reset successfully.")

async def daily_motivation_task():
    """Scheduled task to generate and broadcast daily motivation."""
    logging.info("Running daily motivation broadcast...")
    message = await generate_daily_motivation()

    if "خطا" in message or "ایجاد نشد" in message:
        logging.error(f"Failed to generate motivation: {message}")
        return

    user_ids = database.get_all_user_ids()
    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            logging.error(f"Failed to send motivation to {user_id}: {e}")

    logging.info(f"Daily motivation broadcasted to {len(user_ids)} users.")

async def main():
    database.init_db()

    scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Tehran'))

    # Run every day at 00:00 (Midnight)
    scheduler.add_job(reset_message_counts_task, 'cron', hour=0, minute=0)

    # Run every day at 08:00 AM
    scheduler.add_job(daily_motivation_task, 'cron', hour=8, minute=0)

    scheduler.start()

    logging.info("Bot started. Press Ctrl+C to exit.")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
