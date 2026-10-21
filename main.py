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
    "3min": {"label": "3 Mins - 50 KES", "price": "50 KES", "time": "3 Mins", "desc": "3 MINS QUICK TEASE - Private chat, dirty talk, tease pic, video tease"},
    "5min": {"label": "5 Mins - 100 KES", "price": "100 KES", "time": "5 Mins", "desc": "5 MINS HOT PRIVATE - Private video chat, Cam2Cam, moans, 3 custom pics"},
    "10min": {"label": "10 Mins - 200 KES", "price": "200 KES", "time": "10 Mins", "desc": "10 MINS FULL SHOW - Full video call, nude show, dirty talk, 5 pics + 1 video"},
    "30min": {"label": "30 Mins - 300 KES", "price": "300 KES", "time": "30 Mins", "desc": "30 MINS GIRLFRIEND EXPERIENCE - Unlimited call, full nude, roleplay, fetish friendly"},
}

PAYMENTS = {
    "mpesa": "M-Pesa: 0768125767 - Candy",
    "skrill": "Skrill: mbithey7@gmail.com",
    "binance": "Binance ID: 1282131122"
}

HOW_TO = {
    "mpesa": "HOW TO PAY M-PESA:\n1. M-Pesa -> Send Money\n2. Number: 0768125767\n3. Amount: 50/100/200/300\n4. PIN -> Send\n5. Click I Have Paid here",
    "skrill": "HOW TO PAY SKRILL:\n1. Open Skrill\n2. Send Money\n3. Email: mbithey7@gmail.com\n4. Amount: 0.40/0.80/1.60/2.30 USD\n5. Click I Have Paid here",
    "binance": "HOW TO PAY BINANCE:\n1. Binance -> Pay -> Send\n2. ID: 1282131122\n3. Amount in USDT\n4. Click I Have Paid here"
}

async def show_packages(update, context):
    keyboard = [[InlineKeyboardButton(v["label"], callback_data=f"pkg_{k}")] for k,v in PACKAGES.items()]
    text = "Welcome to Candy's Squash\n\nBaby I'm horny, in bed waiting for you... I'm in my panties only\nChoose how long you want to chat with Candy for:"
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def start(update, context):
    await show_packages(update, context)

async def prices(update, context):
    await show_packages(update, context)

async def pay_cmd(update, context):
    await show_packages(update, context)

async def buttons(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("pkg_"):
        key = data.replace("pkg_", "")
        pkg = PACKAGES.get(key)
        if not pkg:
            return
        context.user_data["pkg"] = key
        keyboard = [
            [InlineKeyboardButton("M-Pesa", callback_data="pay_mpesa")],
            [InlineKeyboardButton("Skrill", callback_data="pay_skrill")],
            [InlineKeyboardButton("Binance", callback_data="pay_binance")],
            [InlineKeyboardButton("Back", callback_data="back")]
        ]
        await query.edit_message_text(f"Chat with Candy for {pkg['time']} - {pkg['price']}\n\n{pkg['desc']}\n\nPrice: {pkg['price']}\nChoose payment:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "back":
        await show_packages(update, context)

    elif data.startswith("pay_"):
        pay_key = data.replace("pay_", "")
        pkg_key = context.user_data.get("pkg", "3min")
        pkg = PACKAGES.get(pkg_key)
        guide = HOW_TO.get(pay_key, "")
        pay_info = PAYMENTS.get(pay_key, "")
        context.user_data["pay"] = pay_key
        keyboard = [
            [InlineKeyboardButton("I Have Paid - Continue", callback_data=f"paid_{pay_key}")],
            [InlineKeyboardButton("Send Screenshot", callback_data="send_ss")]
        ]
        await query.edit_message_text(f"Chat with Candy for {pkg['time']} - {pkg['price']}\n\n{pkg['desc']}\n\n{pay_info}\n\n{guide}", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("paid_"):
        pay_key = data.replace("paid_", "")
        pkg_key = context.user_data.get("pkg", "3min")
        pkg = PACKAGES.get(pkg_key)
        await query.edit_message_text(f"Payment received for Chat with Candy for {pkg['time']} - {pkg['price']}\n\nThank you baby! I'm naked and waiting...\nSend Hi to start {pkg['time']} chat")
        if ADMIN_ID:
            try:
                await context.bot.send_message(chat_id=ADMIN_ID, text=f"AUTO PAID: @{query.from_user.username} ({query.from_user.id}) - {pkg['time']} {pkg['price']} - {pay_key}")
            except:
                pass

    elif data == "send_ss":
        await query.edit_message_text("Send your screenshot here baby. I will approve you in 1 min.")

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
        await query.edit_message_text(f"Rejected {tid}")
        try:
            await context.bot.send_message(chat_id=tid, text="Payment not confirmed baby. Send clear screenshot")
        except:
            pass

async def handle_photo(update, context):
    user = update.effective_user
    pkg_key = context.user_data.get("pkg", "unknown")
    pay_key = context.user_data.get("pay", "unknown")
    pkg = PACKAGES.get(pkg_key, {"time": pkg_key, "price": ""})
    await update.message.reply_text("Screenshot received baby, waiting for approval...")
    if ADMIN_ID:
        keyboard = [[InlineKeyboardButton("APPROVE", callback_data=f"approve_{user.id}"), InlineKeyboardButton("REJECT", callback_data=f"reject_{user.id}")]]
        caption = f"Screenshot from @{user.username} ({user.id})\nChat for {pkg['time']} {pkg['price']} Pay {pay_key}"
        try:
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            await context.bot.send_message(chat_id=ADMIN_ID, text=caption, reply_markup=InlineKeyboardMarkup(keyboard))

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("Bot running")
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("prices", prices))
    application.add_handler(CommandHandler("pay", pay_cmd))
    application.add_handler(CallbackQueryHandler(buttons))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_photo))
    application.run_polling()