# -*- coding: utf-8 -*-
import os
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0") or 0)

app = Flask(__name__)
@app.route('/')
def home():
    return "Candy Bot Live"

# YOUR LINKS
VIP_TELEGRAM = "https://t.me/+eEsiq79bG6k2ODlk"
ONLYFANS_LINK = "https://onlyfans.com/candysquash"

CHAT_PACKAGES = {
    "3min": {"name": "3 Mins Chat", "label": "🍒 3 Mins Chat - 50 KES", "price": "50 Ksh", "amount": "50 Ksh", "duration": "3 Mins"},
    "5min": {"name": "5 Mins Chat", "label": "🔥 5 Mins Chat - 100 KES", "price": "100 Ksh", "amount": "100 Ksh", "duration": "5 Mins"},
    "10min": {"name": "10 Mins Chat", "label": "💋 10 Mins Chat - 200 KES", "price": "200 Ksh", "amount": "200 Ksh", "duration": "10 Mins"},
    "30min": {"name": "30 Mins Chat", "label": "😍 30 Mins Chat - 300 KES", "price": "300 Ksh", "amount": "300 Ksh", "duration": "30 Mins"},
}

VIDEO_PACKAGES = {
    "1vid": {"name": "1 Video", "label": "🎬 1 Video - 150 KES", "price": "150 Ksh", "amount": "150 Ksh", "duration": "1 Video"},
    "3vid": {"name": "3 Videos", "label": "🔥 3 Videos - 300 KES", "price": "300 Ksh", "amount": "300 Ksh", "duration": "3 Videos"},
    "5vid": {"name": "5 Videos + Pics", "label": "💋 5 Videos + 10 Pics - 500 KES", "price": "500 Ksh", "amount": "500 Ksh", "duration": "5 Videos"},
    "10vid": {"name": "10 Videos Pack", "label": "👑 10 Videos Pack - 800 KES", "price": "800 Ksh", "amount": "800 Ksh", "duration": "10 Videos"},
    "lifetime": {"name": "Lifetime Videos", "label": "💦 LIFETIME All Videos - 1500 KES", "price": "1500 Ksh", "amount": "1500 Ksh", "duration": "Lifetime"},
}

PAYMENTS = {
    "mpesa": "M-Pesa: 0768125767 - Candy",
    "skrill": "Skrill: mbithey7@gmail.com",
    "binance": "Binance ID: 1282131122"
}

async def start(update, context):
    context.user_data.clear()
    text = "Welcome to Candy's Squash 🔥\n\nBaby I'm horny, in bed waiting for you... I'm in my panties only 😏💦\n\nWhat do you want baby? 👇"
    keyboard = [
        [InlineKeyboardButton("💬 Chat with Candy - 50-300 KES", callback_data="menu_chat")],
        [InlineKeyboardButton("🎬 Candy's Videos - 150-1500 KES", callback_data="menu_video")]
    ]
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_chat(update, context):
    text = "💬 Chat with Candy 🔥\n\nChoose how long you want to chat with me baby:"
    keyboard = [[InlineKeyboardButton(v["label"], callback_data=f"chat_{k}")] for k,v in CHAT_PACKAGES.items()]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_start")])
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_video(update, context):
    text = "🎬 Candy's Private