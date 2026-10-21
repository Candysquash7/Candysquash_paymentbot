# -*- coding: utf-8 -*-
import os
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0") or 0)

app = Flask(__name__)
@app.route('/')
def home():
    return "Candy Bot Live"

PACKAGES = {
    "3min": {"name": "3 Mins", "label": "🍒 3 Mins - 50 KES", "price": "50 Ksh", "amount": "50 Ksh", "duration": "3 Mins"},
    "5min": {"name": "5 Mins", "label": "🔥 5 Mins - 100 KES", "price": "100 Ksh", "amount": "100 Ksh", "duration": "5 Mins"},
    "10min": {"name": "10 Mins", "label": "💋 10 Mins - 200 KES", "price": "200 Ksh", "amount": "200 Ksh", "duration": "10 Mins"},
    "30min": {"name": "30 Mins", "label": "😍 30 Mins - 300 KES", "price": "300 Ksh", "amount": "300 Ksh", "duration": "30 Mins"},
}

PAYMENTS = {
    "mpesa": "M-Pesa: 0768125767 - Candy",
    "skrill": "Skrill: mbithey7@gmail.com",
    "binance": "Binance ID: 1282131122"
}

async def start(update, context):
    context.user_data.clear()
    text = "Welcome to Candy's Squash 🔥\n\nBaby I'm horny, in bed waiting for you... I'm in my panties only 😏💦\nChoose how long you want to chat with Candy for:"
    keyboard = [[InlineKeyboardButton(v["label"], callback_data=f"pkg_{k}")] for k,v in PACKAGES.items()]
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def buttons(update, context):
    query = update.callback_query
    data = query.data
    await query.answer()
    if data == "back_start":
        await start(update, context)
        return
    if data.startswith("pkg_"):
        key = data.replace("pkg_", "")