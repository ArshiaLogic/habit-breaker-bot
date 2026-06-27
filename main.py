import asyncio
import datetime
from aiogram.types import BufferedInputFile
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


import base64

async def channel_auto_post_task():
    """Scheduled task that runs every minute to check and send dynamic auto posts."""
    now_str = datetime.datetime.now(pytz.timezone("Asia/Tehran")).strftime("%H:%M")
    posts_to_run = database.get_auto_posts_by_time(now_str)

    if not posts_to_run:
        return

    if not config.CHANNEL_ID:
        logging.error("CHANNEL_ID is not configured for auto posts.")
        return

    logging.info(f"Found {len(posts_to_run)} auto posts scheduled for {now_str}.")

    for post in posts_to_run:
        post_id, has_image = post
        logging.info(f"Generating auto post (ID: {post_id}, Image: {has_image})...")

        result = await generate_channel_post(has_image=bool(has_image))

        if "error" in result:
            logging.error(f"Failed to generate auto post {post_id}: {result['error']}")
            # Fallback to text if error includes text
            if "text" in result:
                try:
                    await bot.send_message(chat_id=config.CHANNEL_ID, text=result["text"])
                    logging.info(f"Auto post {post_id} sent as text-only fallback.")
                except Exception as e:
                    logging.error(f"Failed to send text fallback to channel: {e}")
        else:
            try:
                text = result["text"]
                if "image_base64" in result:
                    img_data = base64.b64decode(result["image_base64"])
                    photo = BufferedInputFile(img_data, filename=f"post_{post_id}.jpg")
                    await bot.send_photo(chat_id=config.CHANNEL_ID, photo=photo, caption=text)
                else:
                    await bot.send_message(chat_id=config.CHANNEL_ID, text=text)
                logging.info(f"Auto post {post_id} successfully sent to channel.")
            except Exception as e:
                logging.error(f"Failed to send auto post to channel: {e}")

async def main():
    database.init_db()

    scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Tehran'))

    # Run every day at 00:00 (Midnight)
    scheduler.add_job(reset_message_counts_task, 'cron', hour=0, minute=0)

    # Run every day at 08:00 AM
    scheduler.add_job(daily_motivation_task, 'cron', hour=8, minute=0)

    # Run channel post task everyday at 12:00 PM (Noon)
    scheduler.add_job(channel_auto_post_task, 'cron', minute='*')

    scheduler.start()

    logging.info("Bot started. Press Ctrl+C to exit.")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
