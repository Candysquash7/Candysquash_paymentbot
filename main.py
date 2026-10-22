import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 7193430583

# Flask for Render to stay Live
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "Candy Bot LIVE!"

WELCOME = "Hey I'm Candy 😜💦\n\nI get a little messy if you chat with me... 😈💋\n\nChoose package baby 👇💦"

def keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍒 3 Mins - 50 KES / $1 / 25⭐", callback_data="pkg_3")],
        [InlineKeyboardButton("🔥 5 Mins - 100 KES / $2 / 50⭐", callback_data="pkg_5")],
        [InlineKeyboardButton("💋 10 Mins - 200 KES / $4 / 100⭐", callback_data="pkg_10")],
        [InlineKeyboardButton("😍 30 Mins - 300 KES / $6 / 150⭐", callback_data="pkg_30")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME, reply_markup=keyboard())

async def btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    
    if data.startswith("pkg_"):
        mins = data.split("_")[1]
        pkg = mins + "min"
        await q.edit_message_text(
            f"😍 {mins} Mins Package!\n\nPay now baby 🥵💦\n\nChoose payment 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⭐ Pay with Stars", callback_data=f"stars_{pkg}")],
                [InlineKeyboardButton("💳 Pay with Skrill - mbithey7@gmail.com", callback_data=f"skrill_{pkg}")],
                [InlineKeyboardButton("₿ Pay with Binance - 1282131122", callback_data=f"binance_{pkg}")],
                [InlineKeyboardButton("⬅️ Back", callback_data="back")]
            ])
        )
    elif data == "back":
        await q.edit_message_text(WELCOME, reply_markup=keyboard())
    else:
        # Skrill, Binance, Stars clicked
        await q.edit_message_text(f"💰 You clicked {data} baby!\n\nSend screenshot 📸 Waiting approval!", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ I Have Paid", callback_data="paid")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back")]
        ]))
        # Tell admin
        try:
            await context.bot.send_message(ADMIN_ID, f"💰 CLIENT PAID: @{q.from_user.username} ({q.from_user.id}) - {data}")
        except:
            pass

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(btn))
    print("Bot Running!")
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)