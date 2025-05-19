### Step 6: Telegram Bot Setup

Set up a Telegram bot to serve as the primary input interface:

1. Create a new bot using BotFather on Telegram
2. Note down the bot token and add it to your .env file
3. Implement the Python Telegram bot handler:

```python
# src/interfaces/telegram_bot.py
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to your Personal AI Assistant! You can log various activities using commands:\n"
        "/daily - Log your daily reflection\n"
        "/gym - Log your gym session\n"
        "/bjj - Log your jiu-jitsu training\n"
        "/food - Log your meal\n"
        "/work - Log your work activities\n"
        "/finance - Log financial transaction\n"
        "/invest - Log investment activity\n"
        "/ask - Ask a question to your AI assistant"
    )

async def handle_daily_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Please share your daily reflection. Include details about your mood, energy levels, "
        "sleep quality, and any notable events."
    )

# Implement similar handlers for other log types

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Process incoming messages and route to appropriate handler
    text = update.message.text
    # This will be expanded in Phase 2 with the intelligence layer
    await update.message.reply_text(f"Received your message: {text}")

def run_bot():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("daily", handle_daily_log))
    # Add other command handlers

    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    run_bot()
```
