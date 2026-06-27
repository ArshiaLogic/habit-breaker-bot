import asyncio
import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from states import AdminStates

import config
import database
from ai_handlers import ask_openrouter, edit_with_gemini

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


def get_admin_dashboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 ویراستاری و ارسال دستی", callback_data="admin_manual_post")],
        [InlineKeyboardButton(text="⚙️ تنظیمات محتوای خودکار", callback_data="admin_auto_post_settings")],
        [InlineKeyboardButton(text="📊 آمار دیتابیس", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 ارسال پیام همگانی (Broadcast)", callback_data="admin_broadcast")]
    ])

def get_admin_auto_post_settings_keyboard() -> InlineKeyboardMarkup:
    posts = database.get_all_auto_posts()
    keyboard = []

    for post in posts:
        post_id = post[0]
        time_str = post[1]
        has_image = "🖼 تصویردار" if post[2] else "📝 فقط متن"

        keyboard.append([
            InlineKeyboardButton(text=f"ساعت {time_str} | {has_image}", callback_data="ignore"),
            InlineKeyboardButton(text="🗑 حذف", callback_data=f"del_autopost_{post_id}")
        ])

    keyboard.append([InlineKeyboardButton(text="➕ افزودن محتوای جدید", callback_data="add_autopost")])
    keyboard.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_back")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

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

# ============================
# Admin Handlers
# ============================

@dp.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("شما دسترسی لازم برای این پنل را ندارید.")
        return
    await state.clear()
    await message.answer("ورود به اتاق فرمان 🎛\nلطفا از منوی زیر انتخاب کنید:", reply_markup=get_admin_dashboard())

@dp.callback_query(F.data == "admin_back")
async def handle_admin_back(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != config.ADMIN_ID:
        return
    await state.clear()
    await callback.message.edit_text("اتاق فرمان 🎛", reply_markup=get_admin_dashboard())

@dp.callback_query(F.data == "admin_manual_post")
async def handle_admin_manual_post(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != config.ADMIN_ID:
        return
    await state.set_state(AdminStates.waiting_for_post_text)
    await callback.message.edit_text("متن خام یا ایده‌ات رو بفرست تا جمنای ویراستاریش کنه (برای انصراف /cancel را بزنید):")

@dp.message(StateFilter(AdminStates.waiting_for_post_text))
async def handle_admin_post_input(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("عملیات لغو شد.", reply_markup=get_admin_dashboard())
        return

    if not config.CHANNEL_ID:
        await message.answer("شناسه کانال تنظیم نشده است.")
        await state.clear()
        return

    loading_msg = await message.answer("در حال ویراستاری متن با جمنای... 🧠")
    edited_text = await edit_with_gemini(message.text)

    if "خطا" in edited_text:
        await loading_msg.edit_text(f"مشکلی پیش آمد:\n{edited_text}")
    else:
        try:
            await bot.send_message(chat_id=config.CHANNEL_ID, text=edited_text)
            await loading_msg.edit_text("پیام با موفقیت ویراستاری و در کانال منتشر شد. 🚀")
        except Exception as e:
            await loading_msg.edit_text(f"خطا در ارسال پیام به کانال: {str(e)}")

    await state.clear()

@dp.callback_query(F.data == "admin_auto_post_settings")
async def handle_admin_auto_post_settings(callback: CallbackQuery):
    if callback.from_user.id != config.ADMIN_ID:
        return
    await callback.message.edit_text(
        "لیست محتواهای خودکارِ تنظیم شده برای انتشار در کانال:",
        reply_markup=get_admin_auto_post_settings_keyboard()
    )

@dp.callback_query(F.data.startswith("del_autopost_"))
async def handle_delete_autopost(callback: CallbackQuery):
    if callback.from_user.id != config.ADMIN_ID:
        return
    post_id = int(callback.data.split("_")[-1])
    database.delete_auto_post(post_id)
    await callback.message.edit_text(
        "حذف شد. لیست به‌روزرسانی شده:",
        reply_markup=get_admin_auto_post_settings_keyboard()
    )

@dp.callback_query(F.data == "add_autopost")
async def handle_add_autopost(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != config.ADMIN_ID:
        return
    await state.set_state(AdminStates.waiting_for_post_time)
    await callback.message.edit_text("لطفا ساعت انتشار را به فرمت HH:MM وارد کنید (مثال: 14:30) :\n(برای انصراف /cancel را بزنید)")

@dp.message(StateFilter(AdminStates.waiting_for_post_time))
async def handle_post_time_input(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("عملیات لغو شد.", reply_markup=get_admin_dashboard())
        return

    # Basic validation for HH:MM
    if len(message.text) == 5 and ":" in message.text:
        await state.update_data(time=message.text)
        await state.set_state(AdminStates.waiting_for_post_image_pref)

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="بله، همراه با تصویر ساخته شود", callback_data="pref_img_1")],
            [InlineKeyboardButton(text="خیر، فقط متن باشد", callback_data="pref_img_0")]
        ])
        await message.answer("آیا این محتوا باید همراه با تصویر اختصاصی باشد؟", reply_markup=kb)
    else:
        await message.answer("فرمت زمان نامعتبر است. لطفا به فرمت HH:MM بفرستید (مثال: 08:00).")

@dp.callback_query(StateFilter(AdminStates.waiting_for_post_image_pref), F.data.startswith("pref_img_"))
async def handle_post_img_pref(callback: CallbackQuery, state: FSMContext):
    has_image = int(callback.data.split("_")[-1])
    data = await state.get_data()
    post_time = data.get("time")

    database.add_auto_post(post_time, has_image)
    await state.clear()

    await callback.message.edit_text(
        f"محتوای جدید با موفقیت برای ساعت {post_time} ذخیره شد.\nلیست محتواها:",
        reply_markup=get_admin_auto_post_settings_keyboard()
    )

@dp.callback_query(F.data == "admin_stats")
async def handle_admin_stats(callback: CallbackQuery):
    if callback.from_user.id != config.ADMIN_ID:
        return
    total_users = database.get_total_users()
    await callback.message.answer(f"تعداد کل قهرمان‌های عضو ربات: {total_users} نفر 🏆")
    await callback.answer()

@dp.callback_query(F.data == "admin_broadcast")
async def handle_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != config.ADMIN_ID:
        return
    await state.set_state(AdminStates.waiting_for_broadcast)
    await callback.message.edit_text("پیامی که می‌خوای به پیوی تمام کاربرا ارسال بشه رو بفرست (متن یا عکس):\n(برای انصراف /cancel را بزنید)")

@dp.message(StateFilter(AdminStates.waiting_for_broadcast))
async def handle_admin_broadcast_input(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("عملیات لغو شد.", reply_markup=get_admin_dashboard())
        return

    users = database.get_all_user_ids()
    if not users:
        await message.answer("هیچ کاربری در دیتابیس یافت نشد.")
        await state.clear()
        return

    sent_count = 0
    loading_msg = await message.answer(f"در حال ارسال پیام به {len(users)} کاربر... ⏳")

    for user_id in users:
        try:
            await message.copy_to(chat_id=user_id)
            sent_count += 1
            await asyncio.sleep(0.05) # Prevent hitting rate limits
        except Exception:
            pass # Ignore if user blocked the bot

    await loading_msg.edit_text(f"پیام همگانی با موفقیت به {sent_count} نفر ارسال شد. 🚀")
    await state.clear()


@dp.message(StateFilter(None), F.text)
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

    response_text = await ask_openrouter(message.text)

    if "خطا" not in response_text:
        database.increment_message_count(user_id)

    await loading_msg.edit_text(response_text)
