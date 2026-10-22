import os
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
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
    "videocall": {"label": "📹 Video Call / Facetime", "price_kes": "5000 KES", "price_usd": "$25", "stars": 625, "title": "Video Call / Facetime"},
}

PAYMENTS = {
    "skrill": "💳 Skrill: mbithey7@gmail.com",
    "binance": "₿ Binance ID: 1282131122",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    # ✅ UPDATED WELCOME TEXT
    text = (
        "🔥 Welcome to Candy's Squash 💋\n\n"
        "😏 Baby I'm horny... don't keep me waiting... 🛏️💦\n\n"
        "💬 Sweet Chatting 😍\n"
        "📹 Video Call / Facetime Available - Starting from $25 🥵🔥\n"
        "🎬 For videos join my VIP! 👇\n\n"
        "💋 Choose package baby 👇"
    )
    keyboard = []
    for k, v in PACKAGES.items():
        keyboard.append([InlineKeyboardButton(f"{v['label']} - {v['price_kes']} / {v['price_usd']} / {v['stars']}⭐", callback_data=f"pkg_{k}")])
    keyboard.append([InlineKeyboardButton("🎬 My Videos - VIP Links 🔥", callback_data="vip_only")])
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    # ✅ ADMIN ALERT - You will now see everyone who starts bot
    if ADMIN_ID and update.effective_user.id != ADMIN_ID:
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔔 NEW CLIENT STARTED!\n👤 @{update.effective_user.username} | {update.effective_user.first_name}\n🆔 {update.effective_user.id}")
        except:
            pass

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_start":
        await start(update, context)
        return

    if data == "vip_only":
        text = "🎬 Candy's Private Videos 🔥\n\n👇 Join VIP:"
        keyboard = [
            [InlineKeyboardButton("🔥 JOIN VIP TELEGRAM 💦", url=VIP_TELEGRAM)],
            [InlineKeyboardButton("💦 ONLYFANS 🥵", url=ONLYFANS_LINK)],
            [InlineKeyboardButton("⬅️ Back 💬", callback_data="back_start")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("pkg_"):
        key = data.replace("pkg_", "")
        pkg = PACKAGES.get(key)
        context.user_data["pkg"] = key
        context.user_data["pkg_obj"] = pkg
        
        # ✅ Updated description with video call info
        if key == "videocall":
            desc = "📹 Video Call / Facetime 🥵\n💦 Face to face baby, don't keep me waiting... 🔥"
        else:
            desc = f"💬 Chatting + 📹 Video Call Available from $25 😍\n✨ {pkg['title']} ✨"

        text = f"😍 {pkg['title']} 😍\n\n💰 {pkg['price_kes']} | {pkg['price_usd']} | {pkg['stars']} Stars ⭐\n\n{desc}\n\n👇 Choose pay method baby 💋:"
        keyboard = [
            [InlineKeyboardButton(f"⭐ Pay {pkg['stars']} Stars Instant", callback_data=f"pay_stars_{key}")],
            [InlineKeyboardButton(f"💳 Skrill - {pkg['price_usd']}", callback_data=f"pay_skrill_{key}")],
            [InlineKeyboardButton(f"₿ Binance - {pkg['price_usd']}", callback_data=f"pay_binance_{key}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_start")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        # Admin alert for package click
        if ADMIN_ID and query.from_user.id != ADMIN_ID:
            try:
                await context.bot.send_message(chat_id=ADMIN_ID, text=f"👀 CLIENT CLICKED: @{query.from_user.username} ({query.from_user.id}) - {pkg['label']} - {pkg['price_usd']}")
            except:
                pass
        return

    if data.startswith("pay_"):
        parts = data.split("_")
        pay_key = parts[1]
        pkg_key = parts[2]
        pkg = PACKAGES.get(pkg_key)
        context.user_data["pkg"] = pkg_key
        context.user_data["pkg_obj"] = pkg
        context.user_data["pay"] = pay_key

        if pay_key == "stars":
            try:
                await context.bot.send_invoice(
                    chat