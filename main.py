import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

import database
from ai_handlers import generate_daily_motivation, generate_channel_post
import config
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


async def channel_auto_post_task():
    """Scheduled task to post to the channel if settings allow."""
    logging.info("Running channel auto post check...")
    count_str = database.get_setting('auto_post_count')

    if not count_str or count_str == '0':
        logging.info("Auto post is disabled (0).")
        return

    try:
        count = int(count_str)
    except ValueError:
        return

    # In a real scenario you might stagger these throughout the day.
    # For now, we will post the configured number of times when this task runs.
    # To prevent spamming, we can run them with a delay if count > 1

    if not config.CHANNEL_ID:
        logging.error("CHANNEL_ID is not configured for auto posts.")
        return

    for i in range(count):
        logging.info(f"Generating auto post {i+1}/{count}...")
        post_text = await generate_channel_post()
        if "خطا" not in post_text:
            try:
                await bot.send_message(chat_id=config.CHANNEL_ID, text=post_text)
                logging.info(f"Auto post {i+1} successfully sent to channel.")
            except Exception as e:
                logging.error(f"Failed to send auto post to channel: {e}")
        else:
            logging.error(f"Failed to generate auto post: {post_text}")

async def main():
    database.init_db()

    scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Tehran'))

    # Run every day at 00:00 (Midnight)
    scheduler.add_job(reset_message_counts_task, 'cron', hour=0, minute=0)

    # Run every day at 08:00 AM
    scheduler.add_job(daily_motivation_task, 'cron', hour=8, minute=0)

    # Run channel post task everyday at 12:00 PM (Noon)
    scheduler.add_job(channel_auto_post_task, 'cron', hour=12, minute=0)

    scheduler.start()

    logging.info("Bot started. Press Ctrl+C to exit.")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
