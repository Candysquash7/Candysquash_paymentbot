import os, random
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0") or 0)

app = Flask(__name__)
@app.route('/')
def home():
    return "Candy Bot Live 🍒"

PACKAGES = {
    "3min": {"label": "Chat with Candy for 3 Mins - 50 KES 🍒", "price": "50 KES", "time": "3 Mins", "desc": "✨ 3 MINS QUICK TEASE ✨\nI'm in my tiny panties waiting baby 😏\n- Private chat with Candy\n- Dirty talk + I send you my hot tease pic\n- See my boobs shaking on video tease 💦"},
    "5min": {"label": "Chat with Candy for 5 Mins - 100 KES 🔥", "price": "100 KES", "time": "5 Mins", "desc": "🔥 5 MINS HOT PRIVATE 🔥\nBaby I'm already wet thinking of you 🥵\n- Private video chat - you see me touch myself\n- Cam2Cam - show me yours\n- I moan your name + 3 custom sexy pics just for you"},
    "10min": {"label": "Chat with Candy for 10 Mins - 200 KES 💋", "price": "200 KES", "time": "10 Mins", "desc": "💋 10 MINS FULL SHOW 💋\nYou wanna see everything? I'm naked for you now 😍\n- Full private video call - I'm naked in bed\n- Nude show + dirty talk till you cum\n- I let you control me, tell me what to do\n- 5 custom pics + 1 cum video for you"},
    "30min": {"label": "Chat with Candy for 30 Mins - 300 KES 😍", "price": "300 KES", "time": "30 Mins", "desc": "😍 30 MINS GIRLFRIEND EXPERIENCE 😍\nBe my daddy for 30 mins baby, I'm all yours 💋\n- Unlimited video call, I'm your girlfriend\n- Full nude show, roleplay, fetish okay\n- I stay with you till you cum twice\n- Sexting + pics + videos + I keep your pics private"},
}

HOW_TO_PAY = {
    "mpesa": "💳 HOW TO PAY WITH M-PESA:\n1️⃣ Open M-Pesa\n2️⃣ SEND MONEY\n3️⃣ Number: 0768125767\n4️⃣ Amount: 50/100/200/300\n5️⃣ PIN and Send\n6️⃣ Click 'I Have Paid' here 💋\n\n📱 0768125767 - Candy",
    "skrill": "💳 HOW TO PAY WITH SKRILL:\n1️⃣ Open Skrill\n2️⃣ SEND MONEY\n3️⃣ Email: mbithey7@gmail.com\n4️⃣ Amount: $0.40 / $0.80 / $1.60 / $2.30\n5️⃣ Send and click 'I Have Paid' 💋\n\n📧 mbithey7@gmail.com",
    "binance": "💳 HOW TO PAY WITH BINANCE:\n1️⃣ Binance -> Pay -> Send\n2️⃣ ID: 1282131122\n3️⃣ Amount in USDT\n4️⃣ Send and click 'I Have Paid' 💋\n\n₿ ID: 1282131122"
}

TEASE_LINES = [
    "Baby I'm touching myself thinking of you... come chat with me? 🥵",
    "I'm in bed with only my panties on... you wanna see? 😏",
    "Ugh I'm so horny right now... I need you baby 💦",
    "I just took off my bra... want a pic? Choose a package 😍",
    "My pussy is wet for you baby... let's video now? 🔥"
]

async def show_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(v["label"], callback_data=f"pkg_{k}")] for k,v in PACKAGES.items()]
    tease = random.choice(TEASE_LINES)
    text = f"Welcome to Candy's Squash 🍑💦\n\n{tease}\n\nI'm Candy baby — 22yrs, naughty, in Nairobi and I want you 😍\nI'm waiting naked in bed... how long do you want me for? 👇"
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_packages(update, context)

async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_packages(update, context)

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_packages(update, context)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("pkg_"):
        pkg_key = data.replace("pkg_", "")
        pkg = PACKAGES.get(pkg_key)
        context.user_data["chosen_pkg"] = pkg_key
        keyboard = [
            [InlineKeyboardButton("M-Pesa 🇰🇪", callback_data="pay_mpesa")],
            [InlineKeyboardButton("Skrill 💳", callback_data="pay_skrill")],
            [InlineKeyboardButton("Binance ₿", callback_data="pay_binance")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back")]
        ]
        await query.edit_message_text(
            f"Chat with Candy for {pkg['time']} - {pkg['price']} 😍\n\n{pkg['desc']}\n\n