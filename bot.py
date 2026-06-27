import asyncio
import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, Command

import config
import database
from ai_handlers import ask_deepseek, edit_with_gemini

# Initialize bot and dispatcher
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Reply Keyboard
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="شروع / گزارش لغزش"), KeyboardButton(text="وضعیت من")]
    ],
    resize_keyboard=True,
    persistent=True
)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    database.register_user(message.from_user.id)
    welcome_text = (
        "سلام! به ربات پشتیبان مسیر ترک عادت خوش آمدید.\n"
        "من اینجا هستم تا در این مسیر همراه و حامی شما باشم.\n"
        "لطفا از دکمه‌های زیر برای ثبت وضعیت خود استفاده کنید."
    )
    await message.answer(welcome_text, reply_markup=main_keyboard)

@dp.message(F.text == "شروع / گزارش لغزش")
async def handle_start_relapse(message: Message):
    user_id = message.from_user.id
    database.register_user(user_id)
    database.update_start_date(user_id)
    await message.answer(
        "تاریخ شروع مسیر شما با موفقیت به زمان حال بروزرسانی شد. "
        "هرگز ناامید نشوید، شروع دوباره نشانه قدرت شماست!",
        reply_markup=main_keyboard
    )

@dp.message(F.text == "وضعیت من")
async def handle_status(message: Message):
    user_id = message.from_user.id
    start_date = database.get_start_date(user_id)

    if not start_date:
        await message.answer("شما هنوز مسیری را شروع نکرده‌اید. لطفا دکمه «شروع / گزارش لغزش» را بزنید.")
        return

    now = datetime.datetime.now()
    diff = now - start_date
    days = diff.days
    hours = diff.seconds // 3600

    status_text = f"شما تاکنون {days} روز و {hours} ساعت در مسیر موفقیت بوده‌اید! به همین روند ادامه دهید."
    await message.answer(status_text)

@dp.message(Command("post"))
async def handle_admin_post(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("شما دسترسی لازم برای این دستور را ندارید.")
        return

    # Extract text after /post
    text = message.text.replace("/post", "", 1).strip()

    if not text:
        await message.answer("لطفا متن مورد نظر خود را بعد از دستور /post وارد کنید.")
        return

    if not config.CHANNEL_ID:
        await message.answer("شناسه کانال (CHANNEL_ID) در تنظیمات وارد نشده است.")
        return

    await message.answer("در حال ویراستاری متن با جمنای...")

    edited_text = await edit_with_gemini(text)

    if "خطا" in edited_text:
        await message.answer(f"مشکلی پیش آمد:\n{edited_text}")
        return

    try:
        await bot.send_message(chat_id=config.CHANNEL_ID, text=edited_text)
        await message.answer("پیام با موفقیت ویراستاری و در کانال منتشر شد.")
    except Exception as e:
        await message.answer(f"خطا در ارسال پیام به کانال: {str(e)}")

@dp.message(F.text)
async def handle_user_message(message: Message):
    # Ignore admin commands or button presses here (already handled)
    user_id = message.from_user.id

    # Ensure user is registered before tracking messages
    database.register_user(user_id)

    # Check limit
    current_count = database.get_message_count(user_id)
    if current_count >= 5:
        await message.answer("سهمیه ۵ پیام شما برای امروز به پایان رسیده است. لطفا فردا مجددا تلاش کنید.")
        return

    # User can send message
    loading_msg = await message.answer("در حال فکر کردن...")

    response_text = await ask_deepseek(message.text)

    if "خطا" not in response_text:
        database.increment_message_count(user_id)

    await loading_msg.edit_text(response_text)
