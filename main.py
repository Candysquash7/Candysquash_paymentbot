# -*- coding: utf-8 -*-
import os
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, PreCheckoutQueryHandler
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0") or 0)

app = Flask(__name__)
@app.route('/')
def home():
    return "Candy Bot Live 🔥⭐💵"

VIP_TELEGRAM = "https://t.me/+eEsiq79bG6k2ODlk"
ONLYFANS_LINK = "https://onlyfans.com/candysquash"

PACKAGES = {
    "3min": {
        "label": "🍒 3 Mins",
        "title": "😍 Chat with Candy for 3 Mins 😍",
        "desc": "😍 3 MINS QUICK CHAT 😍\n💋 Dirty chat, sexting, moaning\n🔥 I'm your naughty GF for 3 mins\n\n⚠️ NOTE: Chatting ONLY 💬\n❌ No video call, No pics",
        "price_kes": "50 KES",
        "price_usd": "$1",
        "stars": 25
    },
    "5min": {
        "label": "🔥 5 Mins",
        "title": "😍 Chat with Candy for 5 Mins 😍",
        "desc": "😍 5 MINS HOT CHAT 😍\n💋 Be my daddy for 5 mins\n🔥 Sexting, dirty talk, roleplay\n\n⚠️ NOTE: Chatting ONLY 💬\n❌ No video call, No pics",
        "price_kes": "100 KES",
        "price_usd": "$2",
        "stars": 50
    },
    "10min": {
        "label": "💋 10 Mins",
        "title": "💋 Chat with Candy for 10 Mins 💋",
        "desc": "😍 10 MINS NAUGHTY CHAT 😍\n💋 Be my daddy for 10 mins\n🔥 Sexting, roleplay, fetish chat\n\n⚠️ NOTE: Chatting ONLY 💬\n❌ No video call, No pics",
        "price_kes": "200 KES",
        "price_usd": "$4",
        "stars": 100
    },
    "30min": {
        "label": "😍 30 Mins",
        "title": "😍 Chat with Candy for 30 Mins 😍",
        "desc": "😍 30 MINS GF EXPERIENCE 😍\n💋 Be my daddy for 30 mins\n🔥 Unlimited sexting, roleplay\n\n⚠️ NOTE: Chatting ONLY 💬\n❌ No video call, No pics, No videos",
        "price_kes": "300 KES",
        "price_usd": "$6",
        "stars": 150
    },
}

PAYMENTS = {
    "skrill": "💳 Skrill: mbithey7@gmail.com",
    "binance": "₿ Binance ID: 1282131122 - Pay with Crypto USDT",
    "stars": "⭐ Telegram Stars"
}

async def start(update, context):
    context.user_data.clear()
    text = "🔥 Welcome to Candy's Squash 💋\n\n😏 Baby I'm horny... in bed waiting for you... 🛏️\n👙 I'm in my panties only... 💦\n\n💬 Chatting ONLY - No video call ❌\n🎬 For videos join my VIP!\n\n💬 Choose your chat package baby 👇"
    keyboard = [[InlineKeyboardButton(f"{v['label']} - {v['price_kes']} / {v['price_usd']} / {v['stars']}⭐", callback_data=f"pkg_{k}")] for k,v in PACKAGES.items()]
    keyboard = [[InlineKeyboardButton(f"{v['label']} - {v['price_kes']} / {v['price_usd']} / {v['stars']}⭐", callback_data=f"pkg_{k}")] for k,v in PACKAGES.items()]
    keyboard.append([InlineKeyboardButton("🎬 My Videos - VIP Links 🔥", callback_data="vip_only")])
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

    if data == "vip_only":
        text = "🎬 Candy's Private Videos & Pics 🔥💦\n\n⚠️ Chat packages = Chatting ONLY 💬\n🎬 My videos/nudes are HERE baby 👇😍\n\n👇 Join my VIP:"
        keyboard = [
            [InlineKeyboardButton("🔥 JOIN VIP TELEGRAM - Videos 💦", url=VIP_TELEGRAM)],
            [InlineKeyboardButton("💦 ONLYFANS - All My Nudes 🥵", url=ONLYFANS_LINK)],
            [InlineKeyboardButton("⬅️ Back to Chat 💬", callback_data="back_start")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("pkg_"):
        key = data.replace("pkg_", "")
        pkg = PACKAGES.get(key)
        context.user_data["pkg"] = key
        context.user_data["pkg_obj"] =