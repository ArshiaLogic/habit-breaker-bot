# 🧠 Mind-Reset-AI (Telegram Companion & Auto-Publisher)

A powerful, asynchronous Telegram bot built with `aiogram` (v3) that serves a dual purpose: acting as an empathetic AI companion for users breaking bad habits, and functioning as a fully automated content generation engine for Telegram channels.

## 🚀 Key Features

### 👤 User-Facing Features (Habit Tracking & Counseling)
- **Interactive UI (Inline Keyboards):** A clean, easy-to-use glass menu dashboard.
- **Habit Tracker (Day Counter):** Calculates and displays the exact days/hours of success.
- **AI Counseling (DeepSeek):** Users can chat directly with the AI for psychological support (limited to 5 messages per day to manage API quotas).
- **SOS Protocol:** An immediate, non-API-dependent psychological intervention for moments of weakness.
- **Relapse Management:** A two-step verification system to reset the counter without guilt.

### 👑 Admin & Channel Management (The Automation Engine)
- **Secure Admin Panel:** Restricted access via Telegram User ID.
- **AI Editor (Gemini):** Admin can send raw text/ideas; the bot rewrites, polishes, and automatically publishes the optimized text to the connected channel.
- **Round-Robin API Architecture:** Seamlessly rotates between 5 DeepSeek and 5 Gemini API keys to bypass rate limits and ensure 100% uptime.
- **Automated Scheduler:** Sends daily motivational broadcasts to users.

---

## 💡 Beyond Habit Tracking: The Universal Automation Engine
While this bot was originally designed for psychological support, its underlying architecture is a **universal automated content machine**. 
By tweaking the System Prompts and Scheduler, you can use this exact repository for:
- **Automated Niche Channels:** (Crypto news, Tech blogs, Motivation, etc.) Set the Scheduler to fetch topics, generate articles via Gemini, and post them to your channel automatically 3 times a day.
- **Marketing Automation:** Draft raw promotional ideas and let the Gemini API turn them into engaging, high-converting copywriting before broadcasting.
- **Customer Support Bots:** Replace the habit-tracking logic with FAQ routing, keeping the DeepSeek Round-Robin system for limitless AI customer interaction.

---

## 🛠️ Tech Stack
- **Language:** Python 3
- **Framework:** `aiogram` (v3.x)
- **Database:** `SQLite` (Lightweight, robust, no setup required)
- **Task Scheduling:** `APScheduler`
- **AI Integration:** DeepSeek API & Google Gemini API

---

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/mind-reset-ai.git](https://github.com/your-username/mind-reset-ai.git)
   cd mind-reset-ai

   Install dependencies:

Bash
pip install -r requirements.txt

Bash
python main.py


Developed by @ArshiaLogic.
Feel free to contribute, fork, or use this architecture to build your own automated Telegram empires!
