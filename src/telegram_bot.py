import os
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from src.agent.core import PersonalAIAgent

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Maintain a dictionary for per-chat memory and agent
chat_agents = {}
chat_histories = {}  # chat_id -> list of (role, message)

MAX_HISTORY = 10

def get_agent_for_chat(chat_id):
    if chat_id not in chat_agents:
        chat_agents[chat_id] = PersonalAIAgent()
    return chat_agents[chat_id]

def get_history_for_chat(chat_id):
    if chat_id not in chat_histories:
        chat_histories[chat_id] = []
    return chat_histories[chat_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I'm your personal AI agent. Ask me anything about your life data or the world!",
        reply_markup=ForceReply(selective=True),
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    chat_id = update.effective_chat.id
    await update.message.chat.send_action(action="typing")
    agent = get_agent_for_chat(chat_id)
    history = get_history_for_chat(chat_id)
    # Build context from last 10 messages
    context_str = "\n".join([
        f"{role}: {msg}" for role, msg in history[-MAX_HISTORY:]
    ])
    # Compose the prompt with context
    prompt = f"Context from previous messages (last {MAX_HISTORY}):\n{context_str}\nUser: {user_message}"
    try:
        response = agent.process_query(prompt)
        # Truncate to 300 words
        words = response.split()
        if len(words) > 300:
            response = " ".join(words[:300]) + "..."
    except Exception as e:
        response = f"Sorry, there was an error: {e}"
    # Update history
    history.append(("User", user_message))
    history.append(("Bot", response))
    # Keep only the last MAX_HISTORY*2 messages (user+bot)
    if len(history) > MAX_HISTORY * 2:
        del history[:len(history) - MAX_HISTORY * 2]
    await update.message.reply_text(response)

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set in .env")
        exit(1)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling() 