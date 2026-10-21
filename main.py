import os
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0") or 0)

app = Flask(__name__)

@app.route('/')
def home():
    return "Candy Bot Live 🍒"

PACKAGES = {
    "3min": {"label": "3 Mins - 50 KES 🍒", "price": "50 KES", "time": "3 Mins"},
    "5min": {"label": "5 Mins - 100 KES 🔥", "price": "100 KES", "time": "5 Mins"},
    "10min": {"label": "10 Mins - 200 KES 💋", "price": "200 KES", "time": "10 Mins"},
    "30min": {"label": "30 Mins - 300 KES 😍", "price": "300 KES", "time": "30 Mins"},
}

PAYMENTS = {
    "mpesa": "Lipa na M-Pesa: 0768125767 - Candy",
    "skrill": "Skrill: mbithey7@gmail.com",
    "binance": "Binance / Crypto ID: 1282131122 - Candy"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(v["label"], callback_data=f"pkg_{k}")] for k,v in PACKAGES.items()]
    await update.message.reply_text(
        "Welcome to Candy's Squash 🍑💦\n\nChoose your package baby 👇\nPay via M-Pesa and send screenshot:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("pkg_"):
        pkg_key = data.replace("pkg_", "")
        pkg = PACKAGES.get(pkg_key)
        if not pkg:
            return
        context.user_data["chosen_pkg"] = pkg_key
        keyboard = [
            [InlineKeyboardButton("M-Pesa 🇰🇪", callback_data="pay_mpesa")],
            [InlineKeyboardButton("Skrill 💳", callback_data="pay_skrill")],
            [InlineKeyboardButton("Binance ₿", callback_data="pay_binance")],
        ]
        await query.edit_message_text(
            f"You chose {pkg['time']} - {pkg['price']} 😍\n\nChoose payment method baby 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data.startswith("pay_"):
        pay_key = data.replace("pay_", "")
        pkg_key = context.user_data.get("chosen_pkg", "3min")
        pkg = PACKAGES.get(pkg_key)
        pay_info = PAYMENTS.get(pay_key, "")
        await query.edit_message_text(
            f"You chose {pkg['time']} - {pkg['price']} 😍\n\n{pay_info}\n\nThen send M-Pesa screenshot here and wait for approval 💋\nWaiting for screenshot..."
        )
        if ADMIN_ID:
            user = query.from_user
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🔔 NEW ORDER\nUser: @{user.username} ({user.id})\nPackage: {pkg['time']} - {pkg['price']}\nPayment: {pay_key.upper()}\n{pay_info}\nWaiting for screenshot..."
            )

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("Bot running...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))
    application.run_polling()