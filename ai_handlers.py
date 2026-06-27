import aiohttp
import json
import config


# Global variables for Round-Robin state
_openrouter_index = 0
_gemini_index = 0

def get_next_openrouter_key() -> str:
    """Returns the next OpenRouter API key in a round-robin fashion."""
    global _openrouter_index
    if not config.OPENROUTER_KEYS:
        return ""
    key = config.OPENROUTER_KEYS[_openrouter_index]
    _openrouter_index = (_openrouter_index + 1) % len(config.OPENROUTER_KEYS)
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
OPENROUTER_SYSTEM_PROMPT = (
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

async def ask_openrouter(user_message: str) -> str:
    """Sends a user message to OpenRouter API and returns the empathetic response."""
    key = get_next_openrouter_key()
    if not key:
        return "متاسفانه کلید API برای OpenRouter تنظیم نشده است."

    # We will use DeepSeek's OpenAI compatible API endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }
    payload = {
        "model": config.OPENROUTER_TEXT_MODEL,
        "messages": [
            {"role": "system", "content": OPENROUTER_SYSTEM_PROMPT},
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
        return f"خطای سیستمی در ارتباط با OpenRouter: {str(e)}"

async def generate_daily_motivation() -> str:
    """Generates a short, daily motivational message via DeepSeek."""
    key = get_next_openrouter_key()
    if not key:
        return "پیام انگیزشی به دلیل نبود کلید API OpenRouter ایجاد نشد."

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }
    payload = {
        "model": config.OPENROUTER_TEXT_MODEL,
        "messages": [
            {"role": "system", "content": OPENROUTER_SYSTEM_PROMPT},
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
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_TEXT_MODEL}:generateContent?key={key}"
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


async def generate_image_with_gemini(prompt: str) -> dict:
    """Sends a prompt to Gemini API to generate an image and returns a dict with base64 data or error."""
    key = get_next_gemini_key()
    if not key:
        return {"error": "متاسفانه کلید API برای جمنای تنظیم نشده است."}

    # Endpoint for Imagen models in AI Studio
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_IMAGE_MODEL}:predict?key={key}"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1}
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    try:
                        b64_img = data["predictions"][0]["bytesBase64Encoded"]
                        return {"image_base64": b64_img}
                    except (KeyError, IndexError):
                        return {"error": "خطا در پردازش تصویر دریافتی از جمنای."}
                else:
                    return {"error": f"خطا در ارتباط با سرور جمنای (تصویر): {response.status}"}
    except Exception as e:
        return {"error": f"خطای سیستمی در تولید عکس: {str(e)}"}



async def generate_channel_post(has_image: bool = False) -> dict:
    """
    Generates an engaging channel post using Gemini.
    If has_image is True, it also requests an English prompt for an image, generates the image using Gemini Image Model,
    and returns a dict with 'text' and 'image_base64'.
    Otherwise, returns a dict with just 'text'.
    """
    key = get_next_gemini_key()
    if not key:
        return {"error": "خطا: کلید API برای جمنای تنظیم نشده است."}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_TEXT_MODEL}:generateContent?key={key}"
    headers = {
        "Content-Type": "application/json"
    }

    if has_image:
        prompt = (
            "شما یک روانشناس و مربی ترک عادت هستید. یک پست کوتاه، جذاب و بسیار تاثیرگذار "
            "برای یک کانال تلگرامی بنویسید که به افراد در مسیر ترک عادات مخرب کمک می‌کند. "
            "سپس، یک دستور (Prompt) دقیق به زبان انگلیسی برای تولید یک تصویر مرتبط با این متن بنویسید که نشان‌دهنده آرامش، رهایی یا موفقیت باشد. "
            "پاسخ خود را دقیقا و صرفا با فرمت JSON زیر برگردانید بدون هیچ متن اضافه‌ای:\n"
            "{\n"
            "  \"post_text\": \"متن پست فارسی همراه با ایموجی...\",\n"
            "  \"image_prompt\": \"english prompt for image generation...\"\n"
            "}"
        )
    else:
        prompt = (
            "شما یک روانشناس و مربی ترک عادت هستید. یک پست کوتاه، جذاب و بسیار تاثیرگذار "
            "برای یک کانال تلگرامی بنویسید که به افراد در مسیر ترک عادات مخرب کمک می‌کند. "
            "متن باید شامل یک نکته علمی یا روانشناسی ساده، همراه با راهکار عملی و لحن همدلانه باشد. "
            "حتما از ایموجی‌های مناسب استفاده کنید. متن مستقیما آماده انتشار در کانال باشد."
        )

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=20) as response:
                if response.status == 200:
                    data = await response.json()
                    try:
                        result_text = data["candidates"][0]["content"]["parts"][0]["text"]

                        if has_image:
                            # Parse JSON
                            try:
                                # Clean up markdown formatting if Gemini wrapped it in ```json
                                result_text = result_text.replace("```json", "").replace("```", "").strip()
                                parsed = json.loads(result_text)
                                post_text = parsed.get("post_text", "خطا در استخراج متن.")
                                img_prompt = parsed.get("image_prompt", "")

                                img_data = await generate_image_with_gemini(img_prompt)
                                if "error" in img_data:
                                    return {"error": img_data["error"], "text": post_text}

                                return {"text": post_text, "image_base64": img_data["image_base64"]}

                            except json.JSONDecodeError:
                                return {"error": "پاسخ جمنای فرمت JSON معتبری نداشت."}
                        else:
                            return {"text": result_text}

                    except (KeyError, IndexError):
                        return {"error": "خطا در پردازش پاسخ جمنای برای پست کانال."}
                else:
                    return {"error": f"خطا در ارتباط با سرور جمنای (پست کانال): {response.status}"}
    except Exception as e:
        return {"error": f"خطای سیستمی در ارتباط با جمنای (پست کانال): {str(e)}"}
