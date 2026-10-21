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
    "3min": {
        "label": "🍒 3 Mins - 50 KES",
        "title": "😍 Chat with Candy for 3 Mins 😍 - 50 KES 😍",
        "desc": "😍 3 MINS QUICK CHAT 😍\n💋 Dirty chat, sexting, moaning\n🔥 I'm your naughty GF for 3 mins\n\n⚠️ NOTE: Chatting ONLY 💬\n❌ No video call, No pics\n🎬 For videos/pics join my VIP 👇",
        "price": "50 KES"
    },
    "5min": {
        "label": "🔥 5 Mins - 100 KES",
        "title": "😍 Chat with Candy for 5 Mins 😍 - 100 KES 😍",
        "desc": "😍 5 MINS HOT CHAT 😍\n💋 Be my daddy for 5 mins\n🔥 Sexting, dirty talk, roleplay\n\n⚠️ NOTE: Chatting ONLY 💬\n❌ No video call, No pics\n🎬 For videos/pics join my VIP 👇",
        "price": "100 KES"
    },
    "10min": {
        "label": "💋 10 Mins - 200 KES",
        "title": "💋 Chat with Candy for 10 Mins 💋 - 200 KES 😍",
        "desc": "😍 10 MINS NAUGHTY CHAT 😍\n💋 Be my daddy for 10 mins\n🔥 Sexting, roleplay, fetish chat\n\n⚠️ NOTE: Chatting ONLY 💬\n❌ No video call, No pics\n🎬 For videos/pics join my VIP 👇",
        "price": "200 KES"
    },
    "30min": {
        "label": "😍 30 Mins - 300 KES",
        "title": "😍 Chat with Candy for 30 Mins 😍 - 300 KES 😍",
        "desc": "😍 30 MINS GF EXPERIENCE 😍\n💋 Be my daddy for 30 mins\n🔥 Unlimited sexting, roleplay\n😈 Fetish chat - I'm all yours\n\n⚠️ NOTE: Chatting ONLY 💬\n❌ No video call, No pics, No videos\n🎬 Want my videos/pics? Join VIP OnlyFans/Telegram 👇💦",
        "price": "300 KES"
    },
}

PAYMENTS = {
    "mpesa": "📱 M-Pesa: 0768125767 - Candy 💋",
    "skrill": "💳 Skrill: mbithey7@gmail.com",
    "binance": "₿ Binance ID: 1282131122"
}

async def start(update, context):
    context.user_data.clear()
    text = "🔥 Welcome to Candy's Squash 💋\n\n😏 Baby I'm horny... in bed waiting for you... 🛏️\n👙 I'm in my panties only... 💦\n\n💬 Chatting ONLY - No video call ❌\n🎬 For videos join my VIP!\n\n💬 Choose your chat package baby 👇"
    keyboard = [[InlineKeyboardButton(v["label"], callback_data=f"pkg_{k}")] for k,v in PACKAGES.items()]
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
        context.user_data["pkg_obj"] = pkg
        text = f"{pkg['title']}\n\n{pkg['desc']}\n\n💰 Price: {pkg['price']} 😍\n👇 Choose how to pay baby: 💋"
        keyboard = [
            [InlineKeyboardButton("📱 M-Pesa 🇰🇪", callback_data=f"pay_mpesa_{key}")],
            [InlineKeyboardButton("💳 Skrill 🔥", callback_data=f"pay_skrill_{key}")],
            [InlineKeyboardButton("₿ Binance 💋", callback_data=f"pay_binance_{key}")],
            [InlineKeyboardButton("🎬 Want Videos? VIP Links 🔥", callback_data="vip_only")],
            [InlineKeyboardButton("⬅️ Back 🔙", callback_data="back_start")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("pay_"):
        parts = data.split("_")
        pay_key = parts[1]
        pkg_key = parts[2]
        pkg = PACKAGES.get(pkg_key)
        context.user_data["pkg"] = pkg_key
        context.user_data["pkg_obj"] = pkg
        context.user_data["pay"] = pay_key
        context.user_data["awaiting_phone"] = True
        pay_info = PAYMENTS.get(pay_key, "")
        text = f"💰 Payment Details 💳\n\n📢 Channel: Chat with Candy for {pkg['title']}\n📦 Package: {pkg['label']}\n💵 Amount: {pkg['price']}\n⚠️ CHAT ONLY - No video call ❌\n\n{pay_info}\n\n📱 Send your M-Pesa phone number baby (e.g. 0712345678) 👇💋"
        keyboard = [[InlineKeyboardButton("⬅️ Back 🔙", callback_data=f"pkg_{pkg_key}")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "send_ss":
        await query.edit_message_text("📸 Send your screenshot here baby 😍💦 I will approve in 1 min ⏰🔥")

    elif data.startswith("paid_"):
        pay_key = data.replace("paid_", "")
        pkg = context.user_data.get("pkg_obj")
        phone = context.user_data.get("phone", "")
        text = f"✅ Payment received baby! 💰🥰\n📦 {pkg['label']} - CHAT ONLY 💬\n📱 Phone: {phone} ☎️\n\n💦 Thank you baby! I'm ready... Send Hi to start your {pkg['label']} chat 💋🔥\n\n🎬 Want my videos/pics?\n👇 My VIP Links (separate price):"
        keyboard = [
            [InlineKeyboardButton("🔥 JOIN VIP TELEGRAM 💦", url=VIP_TELEGRAM)],
            [InlineKeyboardButton("💦 ONLYFANS - NAKED 🥵", url=ONLYFANS_LINK)]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        if ADMIN_ID:
            try:
                await context.bot.send_message(chat_id=ADMIN_ID, text=f"💰 CHAT PAID: @{query.from_user.username} ({query.from_user.id}) 📱 {phone} - {pkg['label']} - {pay_key} 🔥")
            except:
                pass

    elif data.startswith("approve_"):
        if query.from_user.id != ADMIN_ID: return
        tid = int(data.replace("approve_", ""))
        await query.edit_message_text(f"✅ Approved {tid} 🥰")
        try:
            text = f"✅ Approved baby! 😍💋 I'm ready for chat, send Hi 🥵💦\n\n⚠️ This package = Chatting ONLY 💬\n🎬 For videos:\n🔥 {VIP_TELEGRAM}\n💦 {ONLYFANS_LINK}"
            keyboard = [[InlineKeyboardButton("🔥 JOIN VIP TELEGRAM 💦", url=VIP_TELEGRAM)],[InlineKeyboardButton("💦 ONLYFANS 🥵", url=ONLYFANS_LINK)]]
            await context.bot.send_message(chat_id=tid, text=text, reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            pass
    elif data.startswith("reject_"):
        if query.from_user.id != ADMIN_ID: return
        tid = int(data.replace("reject_", ""))
        await query.edit_message_text(f"❌ Rejected {tid}")
        try:
            await context.bot.send_message(chat_id=tid, text="❌ Payment not confirmed baby 😔 Send clear screenshot 💋")
        except:
            pass

async def handle_text(update, context):
    if not context.user_data.get("awaiting_phone"):
        await start(update, context)
        return
    phone = update.message.text.strip()
    if len(phone) < 9:
        await update.message.reply_text("❌ Invalid number baby 😔 Send like 0712345678 📱")
        return
    context.user_data["phone"] = phone
    context.user_data["awaiting_phone"] = False
    pkg = context.user_data.get("pkg_obj")
    pay_key = context.user_data.get("pay", "mpesa")
    pay_info = PAYMENTS.get(pay_key, "")
    text = f"💰 Payment Details 💳\n\n📢 Channel: Chat with Candy for {pkg['title']}\n📦 Package: {pkg['label']}\n💵 Amount: {pkg['price']}\n📱 Phone: {phone} ☎️\n⚠️ CHAT ONLY 💬\n\n{pay_info}\n\n📸 Now send screenshot here baby 😍👇"
    keyboard = [[InlineKeyboardButton("✅ I Have Paid 💸", callback_data=f"paid_{pay_key}")],[InlineKeyboardButton("📸 Send Screenshot 🖼️", callback_data="send_ss")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_photo(update, context):
    user = update.effective_user
    pkg = context.user_data.get("pkg_obj", {"label": "unknown"})
    phone = context.user_data.get("phone", "No phone")
    pay = context.user_data.get("pay", "mpesa")
    await update.message.reply_text("📸 Screenshot received baby 💦😍 Waiting for approval... ⏰💋")
    if ADMIN_ID:
        keyboard = [[InlineKeyboardButton("✅ APPROVE 🥰", callback_data=f"approve_{user.id}"), InlineKeyboardButton("❌ REJECT 😔", callback_data=f"reject_{user.id}")]]
        caption = f"📸 CHAT from @{user.username} ({user.id}) 👤\n📱 {phone} ☎️\n📦 {pkg['label']} CHAT ONLY - {pay} 💰"
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