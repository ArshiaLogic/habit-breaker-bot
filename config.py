import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_ID = os.getenv("CHANNEL_ID", "")

# Load DeepSeek Keys
DEEPSEEK_KEYS = [
    os.getenv(f"DEEPSEEK_API_KEY_{i}") for i in range(1, 6)
]
# Filter out empty keys if any
DEEPSEEK_KEYS = [k for k in DEEPSEEK_KEYS if k]

# Load Gemini Keys
GEMINI_KEYS = [
    os.getenv(f"GEMINI_API_KEY_{i}") for i in range(1, 6)
]
# Filter out empty keys if any
GEMINI_KEYS = [k for k in GEMINI_KEYS if k]


# Models Configuration
DEEPSEEK_TEXT_MODEL = os.getenv("DEEPSEEK_TEXT_MODEL", "deepseek-chat")
GEMINI_TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-1.5-flash")
GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "imagen-3.0-generate-001")
