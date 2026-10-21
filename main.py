import os, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

app = Flask(__name__)
@app.route('/')
def home(): return "Candy Bot is Live!"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_web, daemon=True).start()

BOT_TOKEN = os.environ['BOT_TOKEN']
ADMIN_ID = int(os.environ.get('ADMIN_ID', '0'))

PRICES = {
    3: 50,
    5: 100,
    10: 200,
    30: 300
}

WELCOME = """🍒 WELCOME BABY TO CANDY'S PRIVATE CHAT 🍒

Hey babe, I'm online now ❤️
I'm so horny waiting for you...

💋 CHOOSE YOUR TIME BABY:

👉 3 Minutes - 50 KES
👉 5 Minutes - 100 KES
👉 10 Minutes - 200 KES
👉 30 Minutes - 300 KES

Tap a button below to unlock private chat with me 👇

💳 SKRILL: mbithey7@gmail.com
📱 M-PESA: 0768125767
💰 BINANCE / USDT: 1282131122

After you pay, send me screenshot here and I will add you instantly 🥰
Don't keep me waiting baby..."""

def get_menu():
    keyboard = [
        [InlineKeyboardButton(f"3 Mins - {PRICES[3]} KES 🍒", callback_data="buy_3")],
        [InlineKeyboardButton(f"5 Mins - {PRICES[5]} KES 🔥", callback_data="buy_5")],
        [InlineKeyboardButton(f"10 Mins - {PRICES[10]} KES 💋", callback_data="buy_10")],
        [InlineKeyboardButton(f"30 Mins - {PRICES[30]} KES 😍", callback_data="buy_30")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME, reply_markup=get_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    minutes = int(query.data.replace("buy_", ""))
    price = PRICES[minutes]
    await query.message.reply_text(f"Good choice baby 😍\n\nYou selected: {minutes} minutes, {price} KES\n\nPay now to:\nM-PESA: 0768125767\nSKRILL: mbithey7@gmail.com\nBINANCE: 1282131122\n\nAfter paying, send screenshot here ❤️")
    if ADMIN_ID != 0:
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"Payment reported — please verify with M-Pesa before approving.\nUser: {user.first_name} | @{user.username}\nUser ID: {user.id}\nSelected: {minutes} minutes, {price} KES\n\nApprove with: /approve {user.id} {minutes}")
        except: pass

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /approve USER_ID MINUTES")
        return
    try:
        user_id = int(context.args[0])
        minutes = int(context.args[1])
        await context.bot.send_message(chat_id=user_id, text=f"Approved baby! 😍 You have {minutes} minutes with Candy! Enjoy... ❤️")
        await update.message.reply_text(f"Approved {user_id} for {minutes} mins ✅")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

if __name__ == '__main__':
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("approve", approve))
    app_bot.add_handler(CallbackQueryHandler(button_handler))
    print("Bot running...")
    app_bot.run_polling()
