import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ['BOT_TOKEN']

WELCOME = """🍒 WELCOME BABY TO CANDY'S PRIVATE CHAT 🍒

Hey babe, I'm online now ❤️ 
I'm so horny waiting for you...

Choose your payment below to unlock private chat with me 👇

💳 SKRILL: mbithey7@gmail.com
📱 M-PESA: 0768125767
💰 BINANCE / USDT: 1282131122

After you pay, send me screenshot here and I will add you instantly 😘
Don't keep me waiting baby..."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
print("Bot running...")
app.run_polling()
