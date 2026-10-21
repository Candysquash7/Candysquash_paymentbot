import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

app = Flask(__name__)

@app.route('/')
def home():
    return "Candy Bot is Live! 🍒"

PACKAGES = {
    "3min": {"label": "3 Mins - 50 KES 🍒", "price": "50 KES", "time": "3 Mins"},
    "5min": {"label": "5 Mins - 100 KES 🔥", "price": "100 KES", "time": "5 Mins"},
    "10min": {"label": "10 Mins - 200 KES 💋", "price": "200 KES", "time": "10 Mins"},
    "30min": {"label": "30 Mins - 300 KES 😍", "price": "300 KES", "time": "30 Mins"},
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(v["label"], callback_data=k)] for k,v in PACKAGES.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to Candy's Squash 🍑💦\n\nChoose your package baby 👇\nPay via M-Pesa and send screenshot:",
        reply_markup=reply_markup
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pkg = PACKAGES.get(query.data)
    if not pkg:
        return
    user = query.from_user
    # Tell user
    await query.edit_message_text(
        f"You chose {pkg['time']} - {pkg['price']} 😍\n\n"
        f"Lipa na M-Pesa: 0768125767 - Candy\n"
        f"Then send M-Pesa screenshot here and wait for approval 💋"
    )
    # Notify Admin
    if ADMIN_ID:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔔 NEW ORDER\nUser: @{user.username} ({user.id})\n"
                 f"Package: {pkg['time']} - {pkg['price']}\n"
                 f"Waiting for screenshot..."
        )

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("Bot running...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(