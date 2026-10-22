import os, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, PreCheckoutQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7193430583") or 0)

app = Flask(__name__)
@app.route('/')
def home(): return "Candy Live OK"

PACKAGES = {
    "3min": {"label": "🍒 3 Mins", "kes": "50 KES", "usd": "$1", "stars": 25},
    "5min": {"label": "🔥 5 Mins", "kes": "100 KES", "usd": "$2", "stars": 50},
    "10min": {"label": "💋 10 Mins", "kes": "200 KES", "usd": "$4", "stars": 100},
    "30min": {"label": "😍 30 Mins", "kes": "300 KES", "usd": "$6", "stars": 150},
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🔥 Welcome to Candy's Squash 💋\n\n"
        "😏 Baby I'm horny... don't keep me waiting... 🛏️💦\n\n"
        "💬 Sweet Chatting 😍\n"
        "📹 Video Call / Facetime Available - DM me for prices 🥵💋\n"
        "🎬 For videos join my VIP!\n\n"
        "💋 Choose package baby 👇"
    )
    kb = []
    for k,v in PACKAGES.items():
        kb.append([InlineKeyboardButton(f"{v['label']} - {v['kes']} / {v['usd']} / {v['stars']}⭐", callback_data=f"pkg_{k}")])
    kb.append([InlineKeyboardButton("🎬 My Videos - VIP Links 🔥", callback_data="vip_only")])
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
    
    # Tell you when someone starts
    if ADMIN_ID and update.effective_user.id != ADMIN_ID:
        try:
            await context.bot.send_message(ADMIN_ID, f"🔔 NEW CLIENT: @{update.effective_user.username} ({update.effective_user.id}) started bot")
        except: pass

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data

    if d == "back_start":
        await start(update, context)
        return
    if d == "vip_only":
        await q.edit_message_text("🎬 VIP Links:\nTelegram: https://t.me/+eEsiq79bG6k2ODlk\nOnlyFans: https://onlyfans.com/candysquash", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_start")]]))
        return
    
    if d.startswith("pkg_"):
        k = d.replace("pkg_","")
        p = PACKAGES[k]
        context.user_data["pkg"] = k
        text = f"😍 {p['label']} - {p['usd']} 😍\n\n📹 Video Call Available - DM for prices 🥵\n\nChoose payment baby:"
        kb = [[InlineKeyboardButton(f"⭐ Pay {p['stars']} Stars", callback_data=f"pay_stars_{k}")],[InlineKeyboardButton(f"💳 Skrill - {p['usd']}", callback_data=f"pay_skrill_{k}")],[InlineKeyboardButton(f"₿ Binance - {p['usd']}", callback_data=f"pay_binance_{k}")],[InlineKeyboardButton("⬅️ Back", callback_data="back_start")]]
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))
        return

    if d.startswith("pay_"):
        _, method, pkg_key = d.split("_")
        p = PACKAGES[pkg_key]
        if method == "stars":
            try:
                await context.bot.send_invoice(chat_id=q.from_user.id, title=f"{p['label']}", description=f"{p['label']} chat", payload=f"candy_{pkg_key}", provider_token="", currency="XTR", prices=[LabeledPrice(p['label'], p['stars'])])
            except Exception as e:
                await q.edit_message_text(f"Stars error: {e}")
        else:
            info = "Skrill: mbithey7@gmail.com" if method=="skrill" else "Binance ID: 1282131122"
            text = f"💰 Pay {p['usd']} via {info}\n\nAfter paying send screenshot baby 📸"
            kb = [[InlineKeyboardButton("✅ I Have Paid", callback_data=f"paid_{pkg_key}")],[InlineKeyboardButton("⬅️ Back", callback_data=f"pkg_{pkg_key}")]]
            await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))
        return

    if d.startswith("paid_"):
        pkg_key = d.replace("paid_","")
        p = PACKAGES.get(pkg_key, {"label": pkg_key, "usd": "$"})
        await q.edit_message_text(f"✅ Got it baby! Waiting approval for {p['label']} ⏰💋")
        # ✅ NOTIFY YOU - CLIENT SAYS HE PAID
        if ADMIN_ID:
            try:
                await context.bot.send_message(ADMIN_ID, f"💰 CLIENT SAYS PAID!\n👤 @{q.from_user.username} ({q.from_user.id})\n📦 {p['label']} - {p['usd']}\n⏰ Waiting for screenshot!")
            except: pass
        return

    if d.startswith("approve_") or d.startswith("reject_"):
        if q.from_user.id != ADMIN_ID: return
        tid = int(d.split("_")[1])
        if "approve_" in d:
            await q.edit_message_text(f"✅ Approved {tid}")
            try: await context.bot.send_message(tid, "✅ Approved baby! Send Hi to start chat 💋 Don't keep me waiting... 🛏️")
            except: pass
        else:
            await q.edit_message_text(f"❌ Rejected {tid}")
            try: await context.bot.send_message(tid, "❌ Not confirmed, send clear screenshot baby 💋")
            except: pass

async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Screenshot received baby 💦 Waiting approval ⏰")
    # ✅ THIS IS THE NOTIFICATION YOU WANTED BABY!
    if ADMIN_ID:
        pkg_key = context.user_data.get("pkg", "unknown")
        p = PACKAGES.get(pkg_key, {"label": pkg_key})
        kb = [[InlineKeyboardButton("✅ APPROVE", callback_data=f"