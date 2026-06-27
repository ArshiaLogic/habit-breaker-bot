import aiohttp
import config

# Global variables for Round-Robin state
_deepseek_index = 0
_gemini_index = 0

def get_next_deepseek_key() -> str:
    """Returns the next DeepSeek API key in a round-robin fashion."""
    global _deepseek_index
    if not config.DEEPSEEK_KEYS:
        return ""
    key = config.DEEPSEEK_KEYS[_deepseek_index]
    _deepseek_index = (_deepseek_index + 1) % len(config.DEEPSEEK_KEYS)
    return key

def get_next_gemini_key() -> str:
    """Returns the next Gemini API key in a round-robin fashion."""
    global _gemini_index
    if not config.GEMINI_KEYS:
        return ""
    key = config.GEMINI_KEYS[_gemini_index]
    _gemini_index = (_gemini_index + 1) % len(config.GEMINI_KEYS)
    return key

# System prompt for DeepSeek
DEEPSEEK_SYSTEM_PROMPT = (
    "شما یک دستیار هوشمند و همدل هستید که به کاربران فارسی‌زبان در مسیر ترک عادت‌های مخرب "
    "(به ویژه ترک خودارضایی) کمک می‌کنید. لحن شما باید بسیار دوستانه، درک‌کننده، و انگیزه بخش باشد. "
    "از قضاوت کردن بپرهیزید و به جای آن راهکارهای عملی و حمایت روانی ارائه دهید."
)

# System prompt for Gemini (Admin Editor)
GEMINI_SYSTEM_PROMPT = (
    "شما یک ویراستار حرفه‌ای محتوای فارسی هستید. متن ارسالی توسط ادمین را دریافت کرده و آن را "
    "برای انتشار در یک کانال تلگرامی که هدف آن حمایت از افراد در مسیر ترک عادات مخرب است، ویرایش و بهینه‌سازی کنید. "
    "لحن باید جذاب، تاثیرگذار و همدلانه باشد. غلط‌های املایی و نگارشی را اصلاح کنید."
)

async def ask_deepseek(user_message: str) -> str:
    """Sends a user message to DeepSeek API and returns the empathetic response."""
    key = get_next_deepseek_key()
    if not key:
        return "متاسفانه کلید API برای دیپ‌سیک تنظیم نشده است."

    # We will use DeepSeek's OpenAI compatible API endpoint
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": DEEPSEEK_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=20) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return f"خطا در ارتباط با سرور: {response.status}"
    except Exception as e:
        return f"خطای سیستمی در ارتباط با دیپ‌سیک: {str(e)}"

async def generate_daily_motivation() -> str:
    """Generates a short, daily motivational message via DeepSeek."""
    key = get_next_deepseek_key()
    if not key:
        return "پیام انگیزشی به دلیل نبود کلید API دیپ‌سیک ایجاد نشد."

    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": DEEPSEEK_SYSTEM_PROMPT},
            {"role": "user", "content": "لطفا یک پیام انگیزشی و روانشناختی کوتاه (حدود ۲-۳ پاراگراف) برای ادامه مسیر ترک عادت بنویس."}
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=20) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return f"خطا در ایجاد پیام روزانه: {response.status}"
    except Exception as e:
        return f"خطای سیستمی در ایجاد پیام روزانه: {str(e)}"

async def edit_with_gemini(text: str) -> str:
    """Sends raw text to Gemini API for editing and optimization."""
    key = get_next_gemini_key()
    if not key:
        return "متاسفانه کلید API برای جمنای تنظیم نشده است."

    # Using Gemini's REST API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [{
            "parts": [{"text": f"{GEMINI_SYSTEM_PROMPT}\n\nمتن اصلی:\n{text}"}]
        }]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=20) as response:
                if response.status == 200:
                    data = await response.json()
                    try:
                        return data["candidates"][0]["content"]["parts"][0]["text"]
                    except (KeyError, IndexError):
                        return "خطا در پردازش پاسخ جمنای."
                else:
                    return f"خطا در ارتباط با سرور جمنای: {response.status}"
    except Exception as e:
        return f"خطای سیستمی در ارتباط با جمنای: {str(e)}"
