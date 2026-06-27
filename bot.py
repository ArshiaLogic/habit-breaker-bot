import asyncio
import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command

import config
import database
from ai_handlers import ask_deepseek, edit_with_gemini

# Initialize bot and dispatcher
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

def get_main_dashboard(user_id: int) -> InlineKeyboardMarkup:
    """Builds the dynamic inline keyboard dashboard."""
    start_date = database.get_start_date(user_id)

    keyboard = []

    # ردیف اول: فقط اگر شروع نکرده باشد
    if not start_date:
        keyboard.append([InlineKeyboardButton(text="🎯 شروع مسیر پاکی", callback_data="start_journey")])

    # ردیف دوم: گزارش‌گیری و تعامل
    keyboard.append([
        InlineKeyboardButton(text="📊 وضعیت من (روزشمار)", callback_data="my_status"),
        InlineKeyboardButton(text="🧠 مشاوره با هوش مصنوعی", callback_data="ai_consult")
    ])

    # ردیف سوم: اورژانس
    keyboard.append([InlineKeyboardButton(text="🆘 وسوسه شدم! (کمک فوری)", callback_data="emergency_help")])

    # ردیف چهارم: تنظیمات/لغزش و کانال
    keyboard.append([
        InlineKeyboardButton(text="⚠️ گزارش لغزش", callback_data="relapse_prompt"),
        InlineKeyboardButton(text="📢 کانال پشتیبانی", url=config.SUPPORT_CHANNEL_URL)
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_relapse_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Builds the 2-layer relapse confirmation keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ نه، اشتباه شد", callback_data="relapse_cancel"),
            InlineKeyboardButton(text="✅ بله، متاسفانه لغزش داشتم", callback_data="relapse_confirm")
        ]
    ])

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    database.register_user(user_id)

    welcome_text = (
        "سلام! به ربات پشتیبان مسیر ترک عادت خوش آمدید.\n"
        "من اینجا هستم تا در این مسیر همراه و حامی شما باشم.\n"
        "لطفا از منوی زیر برای مدیریت وضعیت خود استفاده کنید."
    )

    # Remove any old reply keyboards by sending a message and deleting it quickly (optional cleanup),
    # Or just rely on the user tapping the new inline buttons.

    await message.answer(welcome_text, reply_markup=get_main_dashboard(user_id))

@dp.callback_query(F.data == "start_journey")
async def handle_start_journey(callback: CallbackQuery):
    user_id = callback.from_user.id
    database.update_start_date(user_id)

    await callback.message.edit_text(
        "مسیرت با موفقیت شروع شد! بهت افتخار می‌کنم. از الان روزشمارِ تو فعاله.",
        reply_markup=get_main_dashboard(user_id)
    )
    await callback.answer("مسیر شروع شد!", show_alert=False)

@dp.callback_query(F.data == "my_status")
async def handle_my_status(callback: CallbackQuery):
    user_id = callback.from_user.id
    start_date = database.get_start_date(user_id)

    if not start_date:
        await callback.answer("هنوز مسیرت رو شروع نکردی!", show_alert=True)
        return

    now = datetime.datetime.now()
    diff = now - start_date
    days = diff.days
    hours = diff.seconds // 3600

    status_text = f"قهرمان، تو الان {days} روز و {hours} ساعته که تو مسیر پاکی هستی! 🏆"

    await callback.message.answer(status_text)
    await callback.answer()

@dp.callback_query(F.data == "ai_consult")
async def handle_ai_consult(callback: CallbackQuery):
    user_id = callback.from_user.id
    current_count = database.get_message_count(user_id)
    remaining = max(0, 5 - current_count)

    if remaining > 0:
        msg = f"من اینجام تا حرفاتو بشنوم. می‌تونی مستقیماً همینجا پیام متنی بدی. (سهمیه امروزِ شما: {remaining} از ۵ پیام باقی‌مانده)."
    else:
        msg = "سهمیه ۵ پیام امروزت تموم شده، اما یادت نره مسیر پاکی ادامه داره!"

    await callback.message.answer(msg)
    await callback.answer()

@dp.callback_query(F.data == "emergency_help")
async def handle_emergency_help(callback: CallbackQuery):
    emergency_text = (
        "نفس عمیق بکش... 🌬\n\n"
        "این وسوسه فقط یک موج گذراست، نه واقعیتِ تو.\n"
        "بیا تمرین ۵-۴-۳-۲-۱ رو با هم انجام بدیم:\n"
        "۵ چیز که الان می‌تونی ببینی رو پیدا کن.\n"
        "۴ چیز که می‌تونی لمس کنی رو حس کن.\n"
        "۳ چیز که می‌تونی بشنوی رو پیدا کن.\n"
        "۲ چیز که می‌تونی بوش رو حس کنی.\n"
        "۱ احساس خوبی که الان در بدنت هست.\n\n"
        "تو قوی‌تر از این لحظه‌ای! بلند شو، جات رو عوض کن و یه لیوان آب خنک بخور. 💧"
    )
    await callback.message.answer(emergency_text)
    await callback.answer("کمک فوری ارسال شد!", show_alert=False)

@dp.callback_query(F.data == "relapse_prompt")
async def handle_relapse_prompt(callback: CallbackQuery):
    await callback.message.edit_text(
        "مطمئنی می‌خوای لغزش رو ثبت کنی و روزشمار از صفر شروع بشه؟",
        reply_markup=get_relapse_confirmation_keyboard()
    )

@dp.callback_query(F.data == "relapse_cancel")
async def handle_relapse_cancel(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_text(
        "خوبه که اشتباه شد! به مسیرت ادامه بده.",
        reply_markup=get_main_dashboard(user_id)
    )

@dp.callback_query(F.data == "relapse_confirm")
async def handle_relapse_confirm(callback: CallbackQuery):
    user_id = callback.from_user.id
    # Reset date to now
    database.update_start_date(user_id)

    await callback.message.edit_text(
        "شکست پایان راه نیست، پیش‌نیازِ پیروزیه. دوباره با هم می‌سازیمش.",
        reply_markup=get_main_dashboard(user_id)
    )
    await callback.answer("لغزش ثبت شد.", show_alert=False)

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
        await message.answer("سهمیه ۵ پیام امروزت تموم شده، اما یادت نره مسیر پاکی ادامه داره!")
        return

    # User can send message
    loading_msg = await message.answer("در حال فکر کردن...")

    response_text = await ask_deepseek(message.text)

    if "خطا" not in response_text:
        database.increment_message_count(user_id)

    await loading_msg.edit_text(response_text)
