import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_ID = os.getenv("CHANNEL_ID", "")

# Load OpenRouter Keys
OPENROUTER_KEYS = [
    os.getenv(f"OPENROUTER_API_KEY_{i}") for i in range(1, 6)
]
# Filter out empty keys if any
OPENROUTER_KEYS = [k for k in OPENROUTER_KEYS if k]

# Load Gemini Keys
GEMINI_KEYS = [
    os.getenv(f"GEMINI_API_KEY_{i}") for i in range(1, 6)
]
# Filter out empty keys if any
GEMINI_KEYS = [k for k in GEMINI_KEYS if k]


# Models Configuration
OPENROUTER_TEXT_MODEL = os.getenv("OPENROUTER_TEXT_MODEL", "openai/gpt-oss-120b:free")
GEMINI_TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-1.5-flash")
GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "imagen-3.0-generate-001")

SUPPORT_CHANNEL_URL = os.getenv('SUPPORT_CHANNEL_URL', 'https://t.me/telegram')
