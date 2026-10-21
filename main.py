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
    return "Candy Bot Live 🔥"

PACKAGES = {
    "3min": {"name": "3 Mins", "label": "🍒 3 Mins - 50 KES", "price": "50 Ksh", "amount": "50 Ksh", "duration": "3 Mins", "desc": "3 MINS QUICK TEASE - Private chat, dirty talk, tease pic"},
    "5min": {"name": "5 Mins", "label": "🔥 5 Mins - 100 KES", "price": "100 Ksh", "amount": "100 Ksh", "duration": "5 Mins", "desc": "5 MINS HOT PRIVATE - Private video chat, Cam2Cam, moans, 3 pics"},
    "10min": {"name": "10 Mins", "label": "💋 10 Mins - 200 KES", "price": "200 Ksh", "amount": "200 Ksh", "duration": "10 Mins", "desc": "10 MINS FULL SHOW - Full video call, nude show, 5 pics + video"},
    "30min": {"name": "30 Mins", "label": "😍 30 Mins - 300 KES", "price": "300 Ksh", "amount": "300 Ksh", "duration": "30 Mins", "desc": "30 MINS GF EXPERIENCE - Unlimited, full nude, roleplay"},
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

async def prices(update, context):
    await start(update, context)

async def pay_cmd(update, context):
    await start(update, context)

async def buttons(update, context):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data.startswith("pkg_"):
        key = data.replace("pkg_", "")
        pkg = PACKAGES.get(key)
        if not pkg:
            return
        context.user_data["pkg"] = key
        context.user_data["awaiting_phone"] = True
        
        text = f"Payment Details\n\nChannel: Chat with Candy for {pkg['name']} - {pkg['price']}\nPackage: {pkg['name']}\nAmount: {pkg['amount']}\nDuration: {pkg['duration']}\n\n{PAYMENTS['mpesa']}\n{PAYMENTS['skrill']}\n{PAYMENTS['binance']}\n\nSend your M-Pesa phone number (e.g. 0712345678):"
        keyboard = [[InlineKeyboardButton("Back", callback_data="back_start")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "back_start":
        await start(update, context)

    elif data.startswith("pay_"):
        pay_key = data.replace("pay_", "")
        pkg_key = context.user_data.get("pkg", "3min")
        pkg = PACKAGES.get(pkg_key)
        context.user_data["pay"] = pay_key
        pay_info = PAYMENTS.get(pay_key, "")
        phone = context.user_data.get("phone", "")
        text = f"Payment Details\n\nChannel: Chat with Candy for {pkg['name']} - {pkg['price']}\nPackage: {pkg['name']}\nAmount: {pkg['amount']}\nDuration: {pkg['duration']}\nPhone: {phone}\n\n{pay_info}\n\nNow send screenshot here"
        keyboard = [
            [InlineKeyboardButton("I Have Paid - Continue", callback_data=f"paid_{pay_key}")],
            [InlineKeyboardButton("Send Screenshot", callback_data="send_ss")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "send_ss":
        await query.edit_message_text("Send your screenshot here baby. I will approve in 1 min.")

    elif data.startswith("paid_"):
        pay_key = data.replace("paid_", "")
        pkg_key = context.user_data.get("pkg", "3min")
        pkg = PACKAGES.get(pkg_key)
        phone = context.user_data.get("phone", "")
        await query.edit_message_text(f"Payment received for Chat with Candy for {pkg['name']} - {pkg['price']}\n\nPhone: {phone}\nThank you baby! I'm naked and waiting...\nSend Hi to start {pkg['duration']} chat")
        if ADMIN_ID:
            try:
                await context.bot.send_message(chat_id=ADMIN_ID, text=f"AUTO PAID: @{query.from_user.username} ({query.from_user.id}) - Phone {phone} - {pkg['name']} {pkg['price']} - {pay_key}")
            except:
                pass

    elif data.startswith("approve_"):
        if query.from_user.id != ADMIN_ID:
            return
        tid = int(data.replace("approve_", ""))
        await query.edit_message_text(f"Approved {tid}")
        try:
            await context.bot.send_message(chat_id=tid, text="Payment Approved baby! I'm ready for you now, send Hi")
        except:
            pass
    elif data.startswith("reject_"):
        if query.from_user.id != ADMIN_ID:
            return
        tid = int(data.replace("reject_", ""))
       