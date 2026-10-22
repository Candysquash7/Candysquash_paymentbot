import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0")) # Your ID
PORT = int(os.getenv("PORT", 10000))

app = Flask(__name__)
@app.route('/')
def home():
    return "Candy Bot is Live 🔥"

PRICES = {
    "5_mins": {"label": "5 Mins - 50 KES", "price": "50 KES", "mins": 5},
    "10_mins": {"label": "10 Mins - 100 KES", "price": "100 KES", "mins": 10},
    "20_mins": {"label": "20 Mins - 200 KES", "price": "200 KES", "mins": 20},
    "30_mins": {"label": "30 Mins - 300 KES", "price": "300 KES", "mins": 30},
}

PAY_DETAILS = """
💳 *PAY VIA M-PESA*
Till Number: `123456` 
Name: Candy
Amount: {price}

After paying, click *I Have Paid* 👇
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(v["label"], callback_data=k)] for k,v in PRICES.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "🔥 *Welcome to Candy's Private Chat* 🔥\n\n"
        "Chat 1-on-1 with me, Candy 😘\n\n"
        "💬 *PRICES - Chat Only:*\n"
        "- 5 Mins - 50 KES\n"
        "- 10 Mins - 100 KES\n"
        "- 20 Mins - 200 KES\n"
        "- 30 Mins - 300 KES\n\n"
        "✅ Discreet | Fast Reply | No Rushing\n"
        "⚠️ Chat Only - No Calls\n\n"
        "Select duration below 👇"
    )
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data in PRICES:
        price_info = PRICES[data]
        keyboard = [
            [InlineKeyboardButton("✅ I Have Paid", callback_data=f"paid_{data}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back")]
        ]
        await query.edit_message_text(
            PAY_DETAILS.format(price=price_info['price']),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data.startswith("paid_"):
        duration_key = data.replace("paid_", "")
        price_info = PRICES[duration_key]
        user = query.from_user
        
        # Tell user
        await query.edit_message_text(
            f"⏳ *Payment Received!*\n\n"
            f"You selected: {price_info['label']}\n"
            f"Waiting for admin approval... Please wait 😘",
            parse_mode='Markdown'
        )
        
        # Send to Admin for approval
        admin_keyboard = [
            [
                InlineKeyboardButton("✅ APPROVE", callback_data=f"approve_{user.id}_{duration_key}"),
                InlineKeyboardButton("❌ REJECT", callback_data=f"reject_{user.id}")
            ]
        ]
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔔 *NEW PAYMENT*\n\nUser: @{user.username} ({user.id})\nName: {user.first_name}\nPackage: {price_info['label']}\n\nApprove?",
            reply_markup=InlineKeyboardMarkup(admin_keyboard),
            parse_mode='Markdown'
        )

    elif data == "back":
        keyboard = [[InlineKeyboardButton(v["label"], callback_data=k)] for k,v in PRICES.items()]
        await query.edit_message_text(
            "Select duration below 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data.startswith("approve_"):
        _, user_id, duration_key = data.split("_", 2)
        price_info = PRICES[duration_key]
        await context.bot.send_message(
            chat_id=int(user_id),
            text=f"✅ *Payment Approved!*\n\nYour {price_info['mins']} mins chat starts NOW! 🔥\nChat with me baby 😘",
            parse_mode='Markdown'
        )
        await query.edit_message_text(f"✅ Approved user {user_id} for {price_info['label']}")
    
    elif data.startswith("reject_"):
        user_id = data.split("_")[1]
        await context.bot.send_message(chat_id=int(user_id), text="❌ Payment not confirmed. Please pay and try again or contact admin.")
        await query.edit_message_text(f"❌ Rejected {user_id}")

def run_bot():
    print("Bot Running!")
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(button_handler))
    app_bot.run_polling()

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=PORT)