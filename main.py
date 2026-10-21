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
    return "Candy Bot Live 🔥"

VIP_TELEGRAM = "https://t.me/+eEsiq79bG6k2ODlk"
ONLYFANS_LINK = "https://onlyfans.com/candysquash"

PACKAGES = {
    "3min": {"name": "3 Mins Chat 💋", "label": "🍒 3 Mins Chat - 50 KES 💦", "price": "50 Ksh", "amount": "50 Ksh", "duration": "3 Mins ⏰"},
    "5min": {"name": "5 Mins Chat 🔥", "label": "🔥 5 Mins Chat - 100 KES 😍", "price": "100 Ksh", "amount": "100 Ksh", "duration": "5 Mins ⏰"},
    "10min": {"name": "10 Mins Chat 💦", "label": "💋 10 Mins Chat - 200 KES 🥵", "price": "200 Ksh", "amount": "200 Ksh", "duration": "10 Mins ⏰"},
    "30min": {"name": "30 Mins Chat 😍", "label": "😍 30 Mins Chat - 300 KES 👑", "price": "300 Ksh", "amount": "300 Ksh", "duration": "30 Mins ⏰"},
}

PAYMENTS = {
    "mpesa": "📱 M-Pesa: 0768125767 - Candy 💋",
    "skrill": "💳 Skrill: mbithey7@gmail.com 🔥",
    "binance": "₿ Binance ID: 1282131122 💰"
}

async def start(update, context):
    context.user_data.clear()
    text = "🔥 Welcome to Candy's Squash 💋\n\n😏 Baby I'm horny... in bed waiting for you... 🛏️\n👙 I'm in my panties only... 💦\n\n💬 Choose how long you want to chat with Candy baby: 👇🥵"
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
        pkg = PACKAGES.get(key)
        context.user_data["pkg"] = key
        context.user_data["pkg_obj"] = pkg
        context.user_data["awaiting_phone"] = True
        text = f"💰 Payment Details 💳\n\n📢 Channel: Chat with Candy for {pkg['name']} - {pkg['price']} 💋\n📦 Package: {pkg['name']} 🎁\n💵 Amount: {pkg['amount']} 💸\n⏰ Duration: {pkg['duration']} ⏳\n\n{PAYMENTS['mpesa']}\n{PAYMENTS['skrill']}\n{PAYMENTS['binance']}\n\n📱 Send your M-Pesa phone number baby 💋 (e.g. 0712345678) 👇"
        keyboard = [[InlineKeyboardButton("⬅️ Back 🔙", callback_data="back_start")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("pay_"):
        pay_key = data.replace("pay_", "")
        pkg = context.user_data.get("pkg_obj")
        phone = context.user_data.get("phone", "")
        pay_info = PAYMENTS.get(pay_key, "")
        context.user_data["pay"] = pay_key
        text = f"💰 Payment Details 💳\n\n📢 Channel: Chat with Candy for {pkg['name']} - {pkg['price']} 💋\n📦 Package: {pkg['name']} 🎁\n💵 Amount: {pkg['amount']} 💸\n⏰ Duration: {pkg['duration']} ⏳\n📱 Phone: {phone} ☎️\n\n{pay_info}\n\n📸 Now send screenshot here baby 😍👇"
        keyboard = [[InlineKeyboardButton("✅ I Have Paid - Continue 💸", callback_data=f"paid_{pay_key}")],[InlineKeyboardButton("📸 Send Screenshot 🖼️", callback_data="send_ss")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "send_ss":
        await query.edit_message_text("📸 Send your screenshot here baby 😍💦 I will approve in 1 min ⏰🔥")
    elif data.startswith("paid_"):
        pay_key = data.replace("paid_", "")
        pkg = context.user_data.get("pkg_obj")
        phone = context.user_data.get("phone", "")
        text = f"✅ Payment received baby! 💰🥰\n📦 For Chat with Candy for {pkg['name']} - {pkg['price']} 💋\n📱 Phone: {phone} ☎️\n\n💦 Thank you baby! I'm naked and waiting... 😏👙\n📩 Send Hi to start {pkg['duration']} chat with me 💋🔥\n\n👑 My VIP Links baby 👇💦"
        keyboard = [[InlineKeyboardButton("🔥 JOIN VIP TELEGRAM 💦", url=VIP_TELEGRAM)],[InlineKeyboardButton("💦 ONLYFANS - NAKED 🥵", url=ONLYFANS_LINK)]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        if ADMIN_ID:
            try:
                await context.bot.send_message(chat_id=ADMIN_ID, text=f"💰💸 CHAT PAID: @{query.from_user.username} ({query.from_user.id}) 📱 Phone {phone} - {pkg['name']} {pkg['price']} - {pay_key} 🔥")
            except:
                pass
    elif data.startswith("approve_"):
        if query.from_user.id != ADMIN_ID: return
        tid = int(data.replace("approve_", ""))
        await query.edit_message_text(f"✅ Approved {tid} 🥰")
        try:
            text = f"✅ Approved baby! 😍💋 I'm ready for you now... Send Hi baby 🥵💦\n\n👑 My VIP Links 👇\n🔥 {VIP_TELEGRAM}\n💦 {ONLYFANS_LINK} 🥰"
            keyboard = [[InlineKeyboardButton("🔥 JOIN VIP TELEGRAM 💦", url=VIP_TELEGRAM)],[InlineKeyboardButton("💦 ONLYFANS 🥵", url=ONLYFANS_LINK)]]
            await context.bot.send_message(chat_id=tid, text=text, reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            pass
    elif data.startswith("reject_"):
        if query.from_user.id != ADMIN_ID: return
        tid = int(data.replace("reject_", ""))
        await query.edit_message_text(f"❌ Rejected {tid} 😔")
        try:
            await context.bot.send_message(chat_id=tid, text="❌ Payment not confirmed baby 😔📸 Send clear screenshot please 💋")
        except:
            pass

async def handle_text(update, context):
    if not context.user_data.get("awaiting_phone"):
        await start(update, context)
        return
    phone = update.message.text.strip()
    if len(phone) < 9:
        await update.message.reply_text("❌ Invalid number baby 😔💋 Send like 0712345678 📱")
        return
    context.user_data["phone"] = phone
    context.user_data["awaiting_phone"] = False
    pkg = context.user_data.get("pkg_obj")
    text = f"💰 Payment Details 💳\n\n📢 Channel: Chat with Candy for {pkg['name']} - {pkg['price']} 💋\n📦 Package: {pkg['name']} 🎁\n💵 Amount: {pkg['amount']} 💸\n⏰ Duration: {pkg['duration']} ⏳\n📱 Phone: {phone} ☎️\n\n💳 Choose payment method baby 👇💋"
    keyboard = [[InlineKeyboardButton("📱 M-Pesa 💸", callback_data="pay_mpesa")],[InlineKeyboardButton("💳 Skrill 💰", callback_data="pay_skrill")],[InlineKeyboardButton("₿ Binance 🪙", callback_data="pay_binance")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_photo(update, context):
    user = update.effective_user
    pkg = context.user_data.get("pkg_obj", {"name": "unknown", "price": ""})
    phone = context.user_data.get("phone", "No phone")
    pay = context.user_data.get("pay", "mpesa")
    await update.message.reply_text("📸 Screenshot received baby 💦😍 Waiting for approval... ⏰💋")
    if ADMIN_ID:
        keyboard = [[InlineKeyboardButton("✅ APPROVE 🥰", callback_data=f"approve_{user.id}"), InlineKeyboardButton("❌ REJECT 😔", callback_data=f"reject_{user.id}")]]
        caption = f"📸💬 CHAT from @{user.username} ({user.id}) 👤\n📱 Phone: {phone} ☎️\n📦 {pkg['name']} {pkg['price']} - {pay} 💰"
        try:
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            await context.bot.send_message(chat_id=ADMIN_ID, text=caption, reply_markup=InlineKeyboardMarkup(keyboard))

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("Bot running 🔥")
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("prices", start))
    application.add_handler(CommandHandler("pay", start))
    application.add_handler(CallbackQueryHandler(buttons))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_photo))
    application.run_polling()