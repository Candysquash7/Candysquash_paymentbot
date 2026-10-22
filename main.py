import os
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, PreCheckoutQueryHandler, ContextTypes
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0") or 0)

app = Flask(__name__)
@app.route('/')
def home():
    return "Candy Bot Live"

VIP_TELEGRAM = "https://t.me/+eEsiq79bG6k2ODlk"
ONLYFANS_LINK = "https://onlyfans.com/candysquash"

PACKAGES = {
    "3min": {"label": "🍒 3 Mins", "price_kes": "50 KES", "price_usd": "$1", "stars": 25, "title": "Chat 3 Mins"},
    "5min": {"label": "🔥 5 Mins", "price_kes": "100 KES", "price_usd": "$2", "stars": 50, "title": "Chat 5 Mins"},
    "10min": {"label": "💋 10 Mins", "price_kes": "200 KES", "price_usd": "$4", "stars": 100, "title": "Chat 10 Mins"},
    "30min": {"label": "😍 30 Mins", "price_kes": "300 KES", "price_usd": "$6", "stars": 150, "title": "Chat 30 Mins"},
}

PAYMENTS = {
    "skrill": "💳 Skrill: mbithey7@gmail.com",
    "binance": "₿ Binance ID: 1282131122",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    try:
        if update.message:
            await update.message.reply_text("✨", reply_markup=ReplyKeyboardRemove())
    except:
        pass

    # ✅ UPDATED - NO PRICE FOR VIDEO CALL, JUST DM FOR PRICES
    text = (
        "🔥 Welcome to Candy's Squash 💋\n\n"
        "😏 Baby I'm horny... don't keep me waiting... 🛏️💦\n\n"
        "💬 Sweet Chatting 😍\n"
        "📹 Video Call / Facetime Available - DM me for prices 🥵💋\n"
        "🎬 For videos join my VIP! 👇\n\n"
        "💋 Choose package baby 👇"
    )
    keyboard = []
    for k, v in PACKAGES.items():
        keyboard.append([InlineKeyboardButton(f"{v['label']} - {v['price_kes']} / {v['price_usd']} / {v['stars']}⭐", callback_data